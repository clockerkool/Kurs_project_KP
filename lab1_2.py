from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from random import randint

import sys
import interface6
import math
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
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.init_widget()
        self.pushButton.clicked.connect(self.plot_widget)
        self.lineEdit.setText("0.5")
        self.lineEdit_2.setText("0.5")
        self.lineEdit_3.setText("0.5")
        self.lineEdit_4.setText("12")
        self.lineEdit_5.setText("14")
        self.lineEdit_6.setText("16")
        self.lineEdit_7.setText("100")
        self.lineEdit_8.setText("1000")
        self.lineEdit_9.setText("0.9")

    def init_widget(self):
        self.matplotlibWidget = MatplotlibWidget()
        self.layoutvertical = QVBoxLayout(self.GraphWidget)
        self.layoutvertical.addWidget(self.matplotlibWidget)
        self.matplotlibWidget2 = MatplotlibWidget()
        self.layoutvertical = QVBoxLayout(self.Graph2)
        self.layoutvertical.addWidget(self.matplotlibWidget2)

    def plot_widget(self):
        # Вероятность смены направления
        self.Px = float(self.lineEdit.text())
        self.Py = float(self.lineEdit_2.text())
        self.Pz = float(self.lineEdit_3.text())

        # Радиусы большого и маленького стержня
        self.R = 30
        self.r = 10

        ALPHA = float(self.lineEdit_9.text())
        M = int(self.lineEdit_8.text())
        N = int(self.lineEdit_7.text())

        self.matplotlibWidget.axis.clear()
        self.matplotlibWidget.axis.set_xscale("log")
        self.matplotlibWidget2.axis.set_xscale("log")

        exp1 = self.ser_exp(M, N)
        for i in range(M):
            self.matplotlibWidget.axis.plot(range(1, N + 1), exp1[i], color='black')

        confidence_interval = self.conf_interval(exp1, ALPHA)
        self.matplotlibWidget.axis.plot(range(1, N + 1), np.mean(exp1, axis=0), color="red")
        self.matplotlibWidget.axis.plot(range(1, N + 1), confidence_interval[0,], color="blue")
        self.matplotlibWidget.axis.plot(range(1, N + 1), confidence_interval[1,], color="blue")

        exp_error = (confidence_interval[1,] - confidence_interval[0,]) / 2

        coef = self.normal_quantile((1 + ALPHA) / 2)
        self.matplotlibWidget2.axis.plot(range(1, N + 1), exp_error, "r--")

        self.label_10.setText(
            self.label_10.text() + f'{np.mean(exp1, axis=0)[-1]} +- {(confidence_interval[1, -1] - confidence_interval[0, -1]) / 2}')
        self.matplotlibWidget.canvas.draw()
        self.matplotlibWidget2.canvas.draw()

    # Проверка, вылетел ли шар из внешнего стержня
    def check_out(self):
        return self.X ** 2 + self.Y ** 2 > self.R ** 2

    # Проверка попал ли шар во внутренний стержень
    def check_in(self):
        return self.X ** 2 + self.Y ** 2 <= self.r ** 2

    # Изменение позции точки
    def rotate_position(self):

        self.X = self.X - 3 if randint(0, 10) <= self.Px * 10 else self.X + 3
        self.Y = self.Y - 3 if randint(0, 10) <= self.Py * 10 else self.Y + 3
        self.Z = self.Z - 3 if randint(0, 10) <= self.Pz * 10 else self.Z + 3

    def exp_2(self, num):
        values = np.zeros(num)
        counter = 0
        for i in range(num):
            # Координаты точки
            self.X = int(self.lineEdit_4.text())
            self.Y = int(self.lineEdit_5.text())
            self.Z = int(self.lineEdit_6.text())

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

    def ser_exp(self, M, N):
        values = np.zeros((M, N))
        for i in range(M):
            values[i,] = self.exp_2(N)
        return values

    def conf_interval(self, vs, alpha):
        m = vs.shape[0]
        a = (1 - alpha) / 2
        m_down = int(m * a)
        m_up = m - m_down - 1
        sorted_vs = np.sort(vs, axis=0)
        return np.apply_along_axis(lambda x: np.array([x[m_down], x[m_up]]), 0, sorted_vs)

    def normal_quantile(self, p):
        return 4.91 * (p ** 0.14 - (1 - p) ** 0.14)


if __name__ == "__main__":
    # M, N = map(int, input().split())
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
