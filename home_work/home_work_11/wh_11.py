class Alphabet:

    def __init__(self, lang, letters):
        self.lang = lang
        self.letters = letters

    def print(self):
        print(self.letters)

    def letters_num(self):
        return len(self.letters)
    
class EngAlphabet(Alphabet):

    _letters_num = 26

    def __init__(self):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        super().__init__("En", letters)

    def is_en_letter(self, letter):
        if letter.upper() in self.letters:
            return True
        else:
            return False

    def letters_num(self):
        return EngAlphabet._letters_num

    @staticmethod
    def example():
        return "This is an example of English text."

if __name__ == "__main__":

    eng = EngAlphabet()

    # 1 Вивести літери
    eng.print()

    # 2 Кількість літер
    print(eng.letters_num())

    # 3 Перевірка F
    print(eng.is_en_letter('F'))

    # 4 Перевірка Щ
    print(eng.is_en_letter('Щ'))

    # 5 Приклад тексту
    print(EngAlphabet.example())