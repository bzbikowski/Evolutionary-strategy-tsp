import random
import math


class Invid:
    """
    Model osobnika
    """
    def __init__(self, init_state=None):
        """
        :param list init_state: dwuelementowa lista zawierająca początkowe wartości
        """
        if init_state is None:
            self.param_values = []
            self.odchylenia = []
        else:
            self.param_values, self.odchylenia = init_state
        self.real_value = 0
        self.track = []
        self.distance = 0
        self.time = 0
        self.cost = 0
        self.value = 0

    def __lt__(self, other):
        return self.value < other.value

    def generate(self, number):
        """
        Wygeneruj ciąg wartości parametrów, ktore są reprezentowane przez liczby rzeczywiste od <-10;10>
        o podanej długości oraz ciąg odchyleń standardowych o tej samej długości.

        :param int number: ilość liczb w wektorach do wygenerowania
        """
        self.param_values = [random.random()*20-10 for _ in range(number)]
        self.odchylenia = [random.random() for _ in range(number)]

    def calculate_value(self, d_matrix, t_matrix, c_matrix):
        """
        Wyznacz przystosowanie osobnika na podstawie jego wektora parametrów.
        Składowe wektora są sortowane i ich kolejność wyznacza trase.

        :param ndarray d_matrix: macierz odległości
        :param ndarray t_matrix: macierz czasu trwania podróży
        :param ndarray c_matrix: macierz kosztów podrózy
        """
        seq = range(len(self.param_values))
        _, seq = zip(*sorted(zip(self.param_values, seq)))
        self.track = seq
        city_pop = -1
        starting_point = -1
        first_city = True
        for city in seq:
            if first_city:
                starting_point = city
                first_city = False
            elif not first_city and self.distance == 0:
                self.distance += d_matrix[starting_point, city]
                self.time += t_matrix[starting_point, city]
                self.cost += c_matrix[starting_point, city]
            else:
                self.distance += d_matrix[city_pop, city]
                self.time += t_matrix[city_pop, city]
                self.cost += c_matrix[city_pop, city]
            city_pop = city
        self.distance += d_matrix[city_pop, starting_point]
        self.time += t_matrix[city_pop, starting_point]
        self.cost += c_matrix[city_pop, starting_point]
        self.value = 1*self.distance + 0.0*self.time + 0.0*self.cost

    def mutation(self):
        """
        Mutacja wektora parametrów oraz wektora odchyleń osobnika
        """
        n = len(self.param_values)
        rand1 = random.normalvariate(0, 1)
        tau = 1/((2*n**(1/2))**(1/2))
        fi = 1/((2 * n) ** (1 / 2))
        for i in range(n):
            rand2 = random.normalvariate(0, 1)
            self.odchylenia[i] *= math.exp(tau*rand2 + fi*rand1)
            if self.odchylenia[i] < 0.1:
                self.odchylenia[i] = 0.1
            rand3 = random.normalvariate(0, self.odchylenia[i])
            self.param_values[i] += rand3


