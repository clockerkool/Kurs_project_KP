from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from random import randint

import sys
import interface6
import numpy as np


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)
        self.layoutvertical = QVBoxLayout(self)
        self.layoutvertical.addWidget(self.canvas)


class MainWindow(QtWidgets.QMainWindow, interface6.Ui_MainWindow):
    def __init__(self, parent=None):
        # Настройка интерфейса
        super(MainWindow, self).__init__(parent=parent)

        self.setupUi(self)
        self.init_widget()
        self.pushButton.clicked.connect(self.plot_widget)

        self.probabylity_X.setText("0.5")
        self.probabylity_Y.setText("0.5")
        self.probabylity_Z.setText("0.5")

        self.coord_X.setText("12")
        self.coord_Y.setText("14")
        self.coord_Z.setText("16")

        self.num_of_exp.setText("100")
        self.num_of_exp_series.setText("1000")
        self.confidence_interval.setText("0.9")

    def init_widget(self):
        # Создание виджетов для графика matplotlib
        self.matplotlibWidget = MatplotlibWidget()
        self.layoutvertical = QVBoxLayout(self.GraphWidget)
        self.layoutvertical.addWidget(self.matplotlibWidget)

        self.matplotlibWidget2 = MatplotlibWidget()
        self.layoutvertical = QVBoxLayout(self.GraphWidget2)
        self.layoutvertical.addWidget(self.matplotlibWidget2)

    def plot_widget(self):
        # Вероятность смены направления
        self.Px = float(self.probabylity_X.text())
        self.Py = float(self.probabylity_Y.text())
        self.Pz = float(self.probabylity_Z.text())

        # Радиусы большого и маленького стержня
        self.R = 30
        self.r = 10

        ALPHA = float(self.confidence_interval.text())
        num_of_exp_series = int(self.num_of_exp_series.text())
        num_of_exp = int(self.num_of_exp.text())

        self.matplotlibWidget.axis.clear()
        self.matplotlibWidget.axis.set_xscale("log")
        self.matplotlibWidget2.axis.set_xscale("log")

        experiment1 = self.ser_exp(num_of_exp_series, num_of_exp)
        for i in range(num_of_exp_series):
            self.matplotlibWidget.axis.plot(range(1, num_of_exp + 1), experiment1[i], color='black')

        confidence_interval = self.conf_interval(experiment1, ALPHA)
        self.matplotlibWidget.axis.plot(range(1, num_of_exp + 1), np.mean(experiment1, axis=0), color="red")
        self.matplotlibWidget.axis.plot(range(1, num_of_exp + 1), confidence_interval[0,], color="blue")
        self.matplotlibWidget.axis.plot(range(1, num_of_exp + 1), confidence_interval[1,], color="blue")

        #Вероятность ошибки
        exp_error_probabylity = (confidence_interval[1,] - confidence_interval[0,]) / 2

        coef = self.normal_quantile((1 + ALPHA) / 2)
        self.matplotlibWidget2.axis.plot(range(1, num_of_exp + 1), exp_error_probabylity, "r--")

        self.label_10.setText(
            self.label_10.text() + f'{np.mean(experiment1, axis=0)[-1]} +- {(confidence_interval[1, -1] - confidence_interval[0, -1]) / 2}')
        self.matplotlibWidget.canvas.draw()
        self.matplotlibWidget2.canvas.draw()

    # Проверка, вылетел ли шар из внешнего стержня
    def check_out(self):
        return self.X ** 2 + self.Y ** 2 > self.R ** 2

    # Проверка попал ли шар во внутренний стержень
    def check_in(self):
        return self.X ** 2 + self.Y ** 2 <= self.r ** 2

    # Изменение позиций точкек
    def rotate_position(self):
        self.X = self.change_position_point(self.X, self.Px)
        self.Y = self.change_position_point(self.Y, self.Py)
        self.Z = self.change_position_point(self.Z, self.Pz)

    # Функция для изменения позиции
    def change_position_point(self, point, probabylity_change):
        return point - 3 if randint(0, 10) <= probabylity_change * 10 else point + 3


    def one_ser_exp(self, num):
        values = np.zeros(num)
        counter = 0
        for i in range(num):
            # Координаты точки
            self.X = int(self.coord_X.text())
            self.Y = int(self.coord_Y.text())
            self.Z = int(self.coord_Z.text())

            N = 0
            while N < 1000:
                self.rotate_position()
                N += 1
                if self.check_out():
                    break
                if self.check_in():
                    counter += 1
                    break
            values[i] = (counter / (i + 1))
        return values

    def ser_exp(self, num_of_ser_exp, num_of_exp):
        values = np.zeros((num_of_ser_exp, num_of_exp))

        for i in range(num_of_ser_exp):
            values[i,] = self.one_ser_exp(num_of_exp)
        return values

    def conf_interval(self, series_of_exp, alpha):
        m = series_of_exp.shape[0]
        a = (1 - alpha) / 2
        m_down = int(m * a)
        m_up = m - m_down - 1
        sorted_vs = np.sort(series_of_exp, axis=0)
        return np.apply_along_axis(lambda x: np.array([x[m_down], x[m_up]]), 0, sorted_vs)

    def normal_quantile(self, p):
        return 4.91 * (p ** 0.14 - (1 - p) ** 0.14)


if __name__ == "__main__":
    # M, N = map(int, input().split())
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
