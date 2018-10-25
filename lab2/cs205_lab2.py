def hello_world():
    print('Hello World')


def find_prime(start: int, end: int):
    result = []
    for i in range(start, end):
        for j in range(2, i):
            if i % j == 0:
                break
        else:
            result.append(i)
    print('the prime between [%d, %d] is :' % (start, end))
    print(result)


class doggy:
    name: str

    def __init__(self, name):
        self.name = name

    def bark(self):
        return self.name + ' bark'


def printer_maker(key):
    def any_name_you_want(gugugu: dict):
        return gugugu[key]
    return any_name_you_want






