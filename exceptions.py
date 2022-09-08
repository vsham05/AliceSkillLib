class WrongSceneNumError(Exception):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return f'''ENG: Scenary named {num} doesn't  exist.
                  RU: Сценарий под номером {num} не существует.'''
