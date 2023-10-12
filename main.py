import sys, random
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QPushButton, QButtonGroup, QRadioButton, QLabel, QTextBrowser


class GenAlgoritmVisualisation(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle('Генетический алгоритм')

        self.generations_field = QTextBrowser(self)
        self.generations_field.setFixedSize(400, 200)
        self.generations_field.move(390, 10)
        
        self.text_len = QLabel(self)
        self.text_len.move(5, 20)
        self.text_len.setText("Введите кол-во особей в одном поколении:")
        
        self.len_population = QLineEdit(self)
        self.len_population.move(5, 45)
        
        self.text_len_c = QLabel(self)
        self.text_len_c.move(5, 70)
        self.text_len_c.setText("Введите кол-во символов в одной особи:")
        
        self.len_char = QLineEdit(self)
        self.len_char.move(5, 100)

        self.results_text = QLabel(self)
        self.results_text.setText("Результаты:")
        self.results_text.move(390, 240)

        self.text_count = QLabel(self)
        self.text_count.move(480, 240)
        self.text_count.setFixedSize(200, 20)

        self.start_button = QPushButton(self)
        self.start_button.clicked.connect(self.start_generate)
        self.start_button.move(280, 100)
        self.start_button.setText("Сгенерировать")

    def start_generate(self):
        self.generations_field.setText('')
        self.generate_population(0, 6, 5)
        
    def generate_character(self, length_character):
        character = ""
        for _ in range(length_character):
            character += str(random.randint(0, 1))
        return character

    def generate_list(self, length_character, length_list):
        list_characters = []
        for _ in range(length_list):
            character = self.generate_character(length_character)
            list_characters.append(character)
        return list_characters

    def success_rate(self, list_characters):
        counter = 0
        for elem in list_characters:
            counter += elem.count("1")
        return counter / len(list_characters)

    def counter(self, character):
        return character.count("1")

    def best_character(self, list_character):
        best_c = "000000"
        c_best_character = 0
        for elem in list_character:
            if c_best_character < self.counter(elem):
                best_c = elem
                c_best_character = self.counter(elem)
        return best_c

    def fight_club(self, list_characters):
        pers1 = random.choice(list_characters)
        pers2 = random.choice(list_characters)
        if self.counter(pers1) > self.counter(pers2):
            return pers1
        else:
            return pers2

    def crossing(self, list_characters):
        offspring_list = []
        for i in range(len(list_characters)):
            gen_crossing = random.randint(0, len(list_characters[i]))
            child = self.fight_club(list_characters)[:gen_crossing] + self.fight_club(list_characters)[gen_crossing:]
            offspring_list.append(child)
        return offspring_list

    def mutation(self, character, chance_mutation):
        mutated_character = ""
        for i in range(len(character)):
            mutation_check = random.randint(0, 1 / (chance_mutation / 100))
            if mutation_check == 1 and character[i] == "0":
                mutated_character += "1"
            elif mutation_check == 1 and character[i] == "1":
                mutated_character += "0"
            else:
                mutated_character += character[i]
        return character

    def mutation_population(self, list_characters, chance_mutation):
        mutated_population = []
        for elem in list_characters:
            m = self.mutation(elem, chance_mutation)
            mutated_population.append(m)
        return mutated_population

    def generation(self, current_population, chance_mutation):
        population = current_population
        parent_population = self.crossing(population)
        mutated_population = self.mutation_population(parent_population, chance_mutation)
        return mutated_population

    def generate_population(self, number_of_generations, len_character, len_population, the_sought_character="",
                            mutation_chance=5):
        find_best_character = False
        len_population = int(self.len_population.text())
        len_character = int(self.len_char.text())
        if the_sought_character == "":
            the_sought_character = "1" * len_character
        generation_counter = 0
        if number_of_generations == 0:
            find_best_character = True
        while number_of_generations > 0 or find_best_character:
            first_population = self.generate_list(len_character, len_population)
            current_population = self.generation(first_population, mutation_chance)

            self.generations_field.insertPlainText(f"{str(current_population)} \n")
            self.generations_field.insertPlainText(f"{str(self.success_rate(current_population))} \n")
            self.generations_field.insertPlainText(f"{self.best_character(current_population)} \n")

            if the_sought_character in current_population and find_best_character:
                self.text_count.setText(f"Количество генераций - {generation_counter + 1}")
                break

            self.generations_field.insertPlainText("\n")

            number_of_generations -= 1
            generation_counter += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GenAlgoritmVisualisation()
    ex.show()
    sys.exit(app.exec_())