from multiprocessing import current_process
import os


def log(message, dirname='logs'):
    process = current_process()

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(f'{dirname}/{process.name.lower()}.log', 'a') as file:
        file.write(f'[{process.name}] {message}\n')
