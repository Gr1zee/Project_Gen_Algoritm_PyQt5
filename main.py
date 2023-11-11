import sys, random, sqlite3
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QMainWindow, QInputDialog, QDialog, QTextBrowser, \
    QVBoxLayout
import pyqtgraph as pg


# pyinstaller --add-data "Gen_alg_ui.ui;generations_db.sqlite;icon.jpg;." main.py

class GenAlgoritmVisualisation(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Gen_alg_ui.ui', self)
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))

        self.action_database.triggered.connect(self.update_database)
        self.action_database_read.triggered.connect(self.read_database)
        self.action_question.triggered.connect(self.about_function)

        self.setWindowTitle("Генетический алгоритм")

        self.start_button.clicked.connect(self.start_generate)
        self.clear_button.clicked.connect(self.clear_all)

        self.count_generation = []
        self.rating = []

        pen = pg.mkPen(color=(255, 0, 0))
        self.graphWidget.plot(self.count_generation, self.rating, pen=pen, symbol="+", symbolSize=20, symbolBrush="b")
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Средний рейтинг генераций")
        self.graphWidget.setLabel("left", "Средний рейтинг генераций")
        self.graphWidget.setLabel("bottom", "Кол-во генераций")

    def about_function(self):
        question = About()
        if question.exec():
            pass
        else:
            pass

    def update_database(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                "Как вас зовут?")

        if ok_pressed and name != "" and self.rating != [] and self.count_generation != []:
            self.user_name = name
        elif name != "":
            self.generations_field.insertPlainText("Ошибка записи в базу данных: Введите имя пользователя")
            return 0
        elif self.rating != [] and self.count_generation != []:
            self.generations_field.insertPlainText("Ошибка записи в базу данных: Произведите генерацию")

        con = sqlite3.connect("generations_db.sqlite")
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO generations(user_name, generation_count, average_rating, len_population, len_character, chance_mutation, rating_lst) VALUES ('{self.user_name}', '{self.generation_counter}', '{round(self.average_rating, 3)}', '{int(self.len_population.text())}', '{int(self.len_char.text())}', '{int(self.chance_mutation.text())}', '{str(self.rating)}')")
        con.commit()
        con.close

    def read_database(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                "Как вас зовут?")

        if ok_pressed and name != "":
            self.user_name = name
            self.clear_all()
        else:
            self.generations_field.insertPlainText("Ошибка чтения из базы данных: Введите имя пользователя")
            return 0

        con = sqlite3.connect("generations_db.sqlite")
        cur = con.cursor()
        res = cur.execute(f"SELECT * FROM generations WHERE  user_name LIKE '{self.user_name}'").fetchall()
        self.db_info = res[0]
        con.close()

        self.text_count.setText(f"Количество генераций - {str(self.db_info[2])}")
        self.text_rating.setText(f"Средний рейтинг всех генераций- {str(self.db_info[3])}")
        self.len_population.setText(str(self.db_info[4]))
        self.len_char.setText(str(self.db_info[5]))
        self.chance_mutation.setText(str(self.db_info[6]))

        pen = pg.mkPen(color=(255, 0, 0))
        x = self.db_info[7].strip('[]').replace(' ', '').split(',')
        x = [float(i) for i in x]
        y = [int(i) for i in range(self.db_info[2] + 1)]

        self.graphWidget.plot(y, x, pen=pen, symbol="o", symbolSize=5, symbolBrush="b")
        self.graphWidget.setBackground('w')

    def clear_all(self):
        self.generations_field.setText('')
        self.len_population.setText('')
        self.len_char.setText('')
        self.chance_mutation.setText('')
        self.text_count.setText('')
        self.count_generation = []
        self.rating = []
        self.graphWidget.clear()

    def start_generate(self):
        self.graphWidget.clear()
        self.count_generation = []
        self.rating = []
        self.generations_field.setText('')
        self.generate_population()

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
            mutation_check = random.randint(0, 1 // (chance_mutation / 100))
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

    def generate_population(self):
        self.rating_a = 0
        try:
            len_population = int(self.len_population.text())
        except Exception:
            self.generations_field.insertPlainText("Ошибка генерации: не указано количество особей в популяции")
            return
        try:
            len_character = int(self.len_char.text())
        except Exception:
            self.generations_field.insertPlainText("Ошибка генерации: не указана длина особи")
            return
        try:
            mutation_chance = int(self.chance_mutation.text())
        except Exception:
            self.generations_field.insertPlainText("Ошибка генерации: не указан шанс мутации")
            return
        try:
            the_sought_character = "1" * len_character
        except Exception:
            self.generations_field.insertPlainText("Ошибка генерации: Слишком болшое число")
        self.generation_counter = 1
        find_best_character = True
        while find_best_character:
            first_population = self.generate_list(len_character, len_population)
            current_population = self.generation(first_population, mutation_chance)

            self.generations_field.insertPlainText(f"{str(current_population)} \n")
            self.generations_field.insertPlainText(f"{str(self.success_rate(current_population))} \n")
            self.rating.append(float(self.success_rate(current_population)))
            self.rating_a += float(self.success_rate(current_population))
            self.generations_field.insertPlainText(f"{self.best_character(current_population)} \n")

            self.count_generation.append(self.generation_counter)

            self.average_rating = self.rating_a / self.generation_counter

            if the_sought_character in current_population and find_best_character:
                self.text_count.setText(f"Количество генераций - {self.generation_counter}")
                self.text_rating.setText(f"Средний рейтинг всех генераций- {round(self.average_rating, 3)}")
                break

            self.generations_field.insertPlainText("\n")

            self.generation_counter += 1

        pen = pg.mkPen(color=(255, 0, 0))
        self.graphWidget.plot(self.count_generation, self.rating, pen=pen, symbol="o", symbolSize=5, symbolBrush="b")
        self.graphWidget.setBackground('w')


class About(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Что такое генетический алгоритм?")
        self.setFixedSize(400, 250)

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        info = QTextBrowser(self)
        info.setText(
            "Генети́ческий алгори́тм (англ. genetic algorithm) — это эвристический алгоритм поиска, используемый для решения задач оптимизации и моделирования путём случайного подбора, комбинирования и вариации искомых параметров с использованием механизмов, аналогичных естественному отбору в природе. Подробнее: https://habr.com/ru/articles/128704/")
        info.setReadOnly(True)
        self.layout.addWidget(info)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = GenAlgoritmVisualisation()
    ex.show()
    sys.exit(app.exec_())
