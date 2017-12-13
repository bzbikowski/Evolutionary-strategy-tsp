import random


class Invid:
    def __init__(self):
        self.param_values = []
        self.real_value = 0
        self.distance = 0
        self.first_city = True

    def generate(self, number):
        """
        Wygeneruj losowy ciąg liczb cakowitych z zakresu  <0,n>
        Taki ciąg będzie repreztował trasę pomiędzy miastami
        :param number: ilość liczb do wygenerowania
        """
        self.param_values = random.choices(range(number), k=number)

    def calculate_distance(self, matrix):
        """

        :param matrix:
        :return:
        """
        city_pop = -1
        starting_point = -1
        for city in self.param_values:
            if self.first_city:
                starting_point = city
                self.first_city = False
            elif not self.first_city and self.distance == 0:
                self.distance += matrix[starting_point, city]
            else:
                self.distance += matrix[city_pop, city]
            city_pop = city
        self.distance += matrix[city_pop, starting_point]

    def mutation(self):
        """

        :return:
        """
        pass

