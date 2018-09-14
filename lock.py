"""
Simple example of Lock usage in threads.

Abstract:
Alice and Bob have some money in Bank accounts.
During concurrent access on same resource threads can face race condition.

Example:
Alice has 1000 USD.
Bob has 1000 USD.

1. Thread 1 wants to transfer 1000 USD from Alice to Bob.
   Transaction should be approved.
2. Thread 2 wants to transfer 1000 USD from Alice to Bob.
   Transaction should be rejected.

Without Lock:
Thread 1 checks if Alice has 1000 USD. Result: True
Thread 2 checks if Alice has 1000 USD. Result: True

Thread 1 transfers 1000 USD from Alice to Bob.
Thread 2 transfers 1000 USD from Alice to Bob.

Result:
Alice has 0 USD.
Bob has 2000 USD.

As you without locking we've created extra 1000 USD from nothing.
"""
from enum import IntEnum
from functools import wraps
from queue import Queue
from threading import Thread, Lock
import time


def lock_method(func):
    """
    Decorator that locks function/method for usage period.
    """
    lock = Lock()

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.USE_LOCK:
            return func(self, *args, **kwargs)

        with lock:
            return func(self, *args, **kwargs)

    return wrapper


class Transaction(object):
    """
    Transaction instance.

    Stores:
        from_account - account from which balance will be consumed
        to_account - account to which balance will be transferred
        amount - balance amount
        status - transaction status
    """
    class STATUS(IntEnum):
        PENDING = 1
        APPROVED = 2
        REJECTED = 3

    def __init__(self, id_, from_account, to_account, amount):
        self.id = id_
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.status = self.STATUS.PENDING
        self.reason = None

    def approve(self):
        self.status = self.STATUS.APPROVED

    def reject(self, reason):
        self.status = self.STATUS.REJECTED
        self.reason = reason

    @property
    def str_status(self):
        for status in self.STATUS:
            if status.real == self.status:
                return status.name


class Bank(object):
    def __init__(self, accounts, use_lock=True):
        self.transactions = Queue()
        self.total_transactions = 0

        self.accounts = accounts
        self.USE_LOCK = use_lock

    @lock_method
    def create_transaction(self, from_account, to_account, amount):
        """
        Creates transaction and adds to queue.

        This method uses lock to prevent duplication of transaction id.

        :param from_account: account name from which balance
                             will be transferred
        :param to_account: account name to which balance will be transferred
        :param amount: balance amount
        :return: Transaction
        """
        transaction_id = self.total_transactions + 1

        transaction = Transaction(transaction_id,
                                  from_account,
                                  to_account,
                                  amount)
        self.transactions.put(transaction)
        self.total_transactions += 1

        return transaction

    @lock_method
    def process_transaction(self, transaction):
        """
        Processes transaction.

        This method uses lock to prevent concurrent changes of account.

        :param transaction: Transaction
        """
        if transaction.from_account not in self.accounts:
            transaction.reject('Sender not found')
        elif transaction.to_account not in self.accounts:
            transaction.reject('Receiver not found')
        elif self.accounts[transaction.from_account] < transaction.amount:
            transaction.reject('Not enough money')
        else:
            # Add little delay between getter and setter of self.accounts
            time.sleep(0.1)

            self.accounts[transaction.from_account] -= transaction.amount
            self.accounts[transaction.to_account] += transaction.amount

            transaction.approve()


class Worker(Thread):
    def __init__(self, bank, transactions):
        super().__init__()

        self.bank = bank
        self.transactions = transactions

    def run(self):
        while not self.transactions.empty():
            from_account, to_account, amount, result = self.transactions.get()

            transaction = self.bank.create_transaction(from_account,
                                                       to_account,
                                                       amount)

            self.bank.process_transaction(transaction)

            if transaction.status == result:
                print(f"[PASSED] From {from_account} to {to_account} balance "
                      f"{amount} - {transaction.str_status}")
            else:
                print(f"[FAILED] From {from_account} to {to_account} balance "
                      f"{amount} - {transaction.str_status} expected "
                      f"{result.name}")

            self.transactions.task_done()


def start(accounts, transactions_, use_lock=True):
    bank = Bank(accounts, use_lock=use_lock)
    transactions = Queue()

    for transaction in transactions_:
        transactions.put(transaction)

    runners = [
        Worker(bank, transactions),
        Worker(bank, transactions),
    ]

    for runner in runners:
        runner.start()

    transactions.join()

    for name, balance in accounts.items():
        print(f"{name}: {balance}")


if __name__ == '__main__':
    ACCOUNTS = {
        'Alice': 2000,
        'Bob': 500,
    }

    TRANSACTIONS = [
        ('Alice', 'Bob', 1500, Transaction.STATUS.APPROVED),
        ('Alice', 'Bob', 1500, Transaction.STATUS.REJECTED),
    ]

    start(ACCOUNTS, TRANSACTIONS, use_lock=True)
