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
        self.param_values = random.sample(range(number), k=number)

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
        mutacja przez inwersje
        :return:
        """
        len_vec_of = random.randint(0, 16)
        number = random.randint(0, 48-len_vec_of)
        vector = self.param_values[number:number+len_vec_of]
        for _ in range(len_vec_of):
            self.param_values.pop(number)
        for item in vector:
            self.param_values.insert(number, item)

