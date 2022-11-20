from os import system, chdir
from os.path import dirname
from sys import argv
from subprocess import Popen
from time import sleep
from random import random

chdir(dirname(argv[0]))
server = Popen(['python', 'server.py'], shell=False, stdin=None)
try:
    while True:
        system(f'python client.py {random()}')
        sleep(2)
except KeyboardInterrupt:
    server.kill()