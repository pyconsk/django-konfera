import string
import random


def random_string(length=1, unicode=False):
    """
    Returns random ascii or unicode string.
    """
    if unicode:
        def random_fun():
            return chr(random.choice((0x300, 0x2000)) + random.randint(0, 0xff))
    else:
        def random_fun():
            return random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

    return ''.join(random_fun() for _ in range(length))
