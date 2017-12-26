import random


class Invid:
    def __init__(self, init_state=None):
        if init_state is None:
            self.param_values = []
        else:
            self.param_values = init_state
        self.real_value = 0
        self.distance = 0
        self.time = 0
        self.cost = 0
        self.value = 0

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def generate(self, number):
        """
        Wygeneruj losowy ciąg liczb cakowitych z zakresu  <0,n>
        Taki ciąg będzie repreztował trasę pomiędzy miastami
        :param number: ilość liczb do wygenerowania
        """
        self.param_values = random.sample(range(number), k=number)

    def calculate_value(self, d_matrix, t_matrix):
        """
        wylicz stopień przystosowania osobnika, czyli jego łącznej sumy odległości oraz czasu
        todo dobrać wagi do tych wartości?
        :param d_matrix:
        :param t_matrix:
        """
        city_pop = -1
        starting_point = -1
        first_city = True
        for city in self.param_values:
            if first_city:
                starting_point = city
                first_city = False
            elif not first_city and self.distance == 0:
                self.distance += d_matrix[starting_point, city]
                self.time += t_matrix[starting_point, city]
            else:
                self.distance += d_matrix[city_pop, city]
                self.time += t_matrix[city_pop, city]
            city_pop = city
        self.distance += d_matrix[city_pop, starting_point]
        self.time += t_matrix[city_pop, starting_point]
        self.value = self.distance + self.time

    def mutation(self):
        """
        wykonaj operację mutacji na osobniku
        """
        # inwersja
        # lenght = len(self.param_values)
        # len_vec_of = random.randint(0, lenght)
        # number = random.randint(0, lenght-len_vec_of)
        # vector = self.param_values[number:number+len_vec_of]
        # for _ in range(len_vec_of):
        #     self.param_values.pop(number)
        # for item in vector:
        #     self.param_values.insert(number, item)

        # wstawienie
        # lenght = len(self.param_values)
        # rand1 = random.randrange(0, lenght)
        # rand2 = random.randrange(0, lenght-1)
        # value = self.param_values.pop(rand1)
        # self.param_values.insert(rand2, value)

        # przestawienie
        lenght = len(self.param_values)
        len_vec_of = random.randint(0, lenght)
        number = random.randint(0, lenght - len_vec_of)
        vector = self.param_values[number:number + len_vec_of]
        for _ in range(len_vec_of):
            self.param_values.pop(number)
        for i, item in enumerate(vector):
            self.param_values.insert(number+i, item)

