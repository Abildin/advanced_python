CURRENCIES = {
    "USD": 1.00,
    "EUR": 0.87,
    "RUB": 65.59,
    "BYN": 2.11,
}


class Currency(object):
    def __init__(self, amount, currency='USD'):
        amount = float(amount)
        currency = currency.upper()

        if currency not in CURRENCIES:
            raise Exception(f'Invalid currency "{currency}".')

        self.amount = amount
        self.currency = currency

    def convert_to_currency(self, currency):
        currency = currency.upper()

        if currency not in CURRENCIES:
            raise Exception(f'Invalid currency "{currency}".')

        amount = self.amount / CURRENCIES[self.currency] * CURRENCIES[currency]

        return Currency(amount, currency)

    def __str__(self):
        return f'{self.amount:.2f} {self.currency}'

    def __add__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't add {other.__class__.__name__} to Money.")

        other = other.convert_to_currency(self.currency)

        return Currency(self.amount + other.amount, self.currency)

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self

        return self + other

    def __sub__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't subtract {other.__class__.__name__} from Money.")

        other = other.convert_to_currency(self.currency)

        return Currency(self.amount - other.amount, self.currency)

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        if not isinstance(other, float) and not isinstance(other, int):
            raise Exception(f"Can't multiply Money to {other.__class__.__name__}.")

        return Currency(self.amount * other, self.currency)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if not isinstance(other, float) and not isinstance(other, int):
            raise Exception(f"Can't divide Money to {other.__class__.__name__}.")

        return Currency(self.amount / other, self.currency)

    def __rtruediv__(self, other):
        return self / other

    def __floordiv__(self, other):
        if not isinstance(other, float) and not isinstance(other, int):
            raise Exception(f"Can't divide Money to {other.__class__.__name__}.")

        return Currency(self.amount // other, self.currency)

    def __rfloordiv__(self, other):
        return self // other

    def __eq__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't compare Money with {other.__class__.__name__}.")

        other = other.convert_to_currency(self.currency)

        return self.amount == other.amount

    def __gt__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't compare Money with {other.__class__.__name__}.")

        other = other.convert_to_currency(self.currency)

        return self.amount > other.amount

    def __ge__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't compare Money with {other.__class__.__name__}.")

        other = other.convert_to_currency(self.currency)

        return self.amount >= other.amount

    def __lt__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't compare Money with {other.__class__.__name__}.")

        other = other.convert_to_currency(self.currency)

        return self.amount < other.amount

    def __le__(self, other):
        if not isinstance(other, Currency):
            raise Exception(f"Can't compare Money with {other.__class__.__name__}.")

        other = other.convert_to_currency(self.currency)

        return self.amount <= other.amount


byn = Currency(1, 'BYN')
eur = Currency(2, 'EUR')

print(byn)
print(eur - byn)
print(byn < eur)

currencies = [Currency(12), Currency(5, 'EUR') * 2.12, Currency(23, 'BYN') / 2.1]

print(sum(currencies))
