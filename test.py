import threading
from time import *


def work():
    print('just a moment...')
    sleep(5)
    print('somma')


thread = threading.Thread(target=work)
thread.start()

boolean = True
num = 0
while boolean:
    print('relaxing...')
    sleep(1)
    num = num  + 1
    if num == 2:
        boolean = False