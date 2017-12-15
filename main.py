'''
3. Rozwiązać problem komiwojażera:
    d) strategią ewolucyjną (µ+λ)
W rozwiązywanym problemie przyjąć, iż nie wszystkie połączenia między dowolnymi
miastami są dopuszczalne. Zastosować odpowiednia reprezentację rozwiązania.
Przyjąć funkcje kryterialną złożoną z kilku wskaźników np. droga, czas, opłaty za
przejazd itp.

Komiwojażer musi odwiedzić każde miasto oraz wrócić do pozycji startowej przy jak najmniejszym koszcie

Strategia (µ+λ) - z populacji (µ+λ) wybieramy µ najlepszych osobników, λ to potomstwo
'''
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from pop import Invid


class Genetic:
    def __init__(self, path_names, path_xy):
        self.c_names = []
        self.c_states = []
        self.c_dist = []
        self.dist_matrix = []
        self.refactor_data(path_names, path_xy)
        self.calc_dist_matrix()

    def refactor_data(self, names_path, xy_path):
        """
        Wczytywanie z pliku nazw miast, które wykorzystujemy w tym projekcie
        Wczytaj z pliku współrzędne każdego miasta na mapie geograficnzej

        :return: city_names - lista nazwm miast
                 data - macierz dwukolumnowa, która dla każdego miasta przechowuje punkt współrzędnych x i y
        """
        with open(names_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split(", ")
                if parts[0] == '\n':
                    break
                self.c_names.append(parts[0])
                self.c_states.append(parts[1][:-1])
        self.c_dist = np.loadtxt(xy_path)

    def calc_dist(self, xx, yy):
        """
        Na podstawie dwóch punktów policz ich odległość Euklidesową

        :param xx: współrzędne 1. punktu
        :param yy: współrzędne 2. punktu

        :return: rzeczywisty dystans na mapie pomiędzy dwoma miastami
        """
        return ((xx[0]-yy[0])**2+(xx[1]-yy[1])**2)**(1/2)

    def calc_dist_matrix(self, break_param=0):
        """
        Wylicz odległości pomiędzy miastami, z uwzględnieniem warunku, że nie wszystkie drogi są przejezdne

        :param distance: macierz zawierająca współrzędne miast
        :param break_param: współczynnik, który oznacza jak często nie będzie danej drogi pomiędzy miastami

        :return: dist_matrix - macierz odległości każdego miasta z każdym miastem
        """
        self.dist_matrix = np.zeros((len(self.c_dist), len(self.c_dist)))
        for ind1, item1 in enumerate(self.c_dist):
            for ind2, item2 in enumerate(self.c_dist):
                if ind1 == ind2:
                    self.dist_matrix[ind1][ind2] = 0
                else:
                    val = random.random()
                    if val < break_param:
                        self.dist_matrix[ind1][ind2] = 99999999999999
                    else:
                        self.dist_matrix[ind1][ind2] = self.calc_dist(item1, item2)

    def start_algorithm(self, start_pop=10, no_of_gen=1000, mutation=0.05):
        """
        strategia ewolucyjna narazie tylko dla odległości pomiędzy miastami
        :param mutation:
        :param start_pop:
        :param no_of_gen:
        :return:
        """
        liczba_osobnikow = start_pop
        liczba_pokolen = no_of_gen
        populacja = []
        lenght = len(self.c_dist)
        self.min = 999999999
        self.min_ciag = None
        for i in range(liczba_osobnikow):
            populacja.append(Invid())
            populacja[i].generate(len(self.dist_matrix))
            populacja[i].calculate_distance(self.dist_matrix)
        while liczba_pokolen > 0:
            if liczba_pokolen % 10 == 0:
                print(liczba_pokolen)
            ############################################
            #               KRZYŻOWANIE
            childrens = []
            copy_pop = np.copy(populacja)
            for _ in range(math.floor(len(populacja)/2)):
                dziecko = []
                nums = random.sample(range(0, len(copy_pop)), k=2)
                krzyzowanie = [copy_pop[nums[0]], copy_pop[nums[1]]]
                copy_pop = np.delete(copy_pop, nums)
                # wyznacz jednego losowego rodzica
                start = krzyzowanie[0] if random.random() > 0.5 else krzyzowanie[1]
                random_city = random.randint(0, lenght-1)
                param = start.param_values[random_city]
                # dodaj losowe miasto z jego ścieżki jako pierwszy element
                dziecko.append(param)
                for i in range(47):
                    val1 = krzyzowanie[0].param_values.index(param)
                    val2 = krzyzowanie[1].param_values.index(param)
                    min1 = val1 - 1
                    if min1 < 0:
                        min1 = lenght - 1  # ostatni element
                    max1 = val1 + 1
                    if max1 > lenght - 1:
                        max1 = 0
                    min2 = val2 - 1
                    if min2 < 0:
                        min2 = lenght - 1
                    max2 = val2 + 1
                    if max2 > lenght - 1:
                        max2 = 0
                    # sprawdź poprawność
                    values = [min1, min2, max1, max2]
                    neigh = [krzyzowanie[0].param_values[min1], krzyzowanie[1].param_values[min2],
                             krzyzowanie[0].param_values[max1], krzyzowanie[1].param_values[max2]]
                    dist_vector = [self.dist_matrix[dziecko[i]][j] for j in neigh]
                    values, dist_vector = (list(x) for x in zip(*sorted(zip(values, dist_vector), key=lambda pair: pair[1])))
                    found = False
                    for j in range(len(dist_vector)):
                        if values[j] not in dziecko:
                            param = values[j]
                            dziecko.append(param)
                            found = True
                            break
                    if not found:
                        # znajdź najbliższe możliwe miasto
                        search = [j for j in range(lenght) if j not in dziecko]
                        min = 999999999999999
                        min_index = -1
                        for j in search:
                            if self.dist_matrix[dziecko[i]][j] < min:
                                min = self.dist_matrix[dziecko[i]][j]
                                min_index = j
                        param = min_index
                        dziecko.append(param)
                childrens.append(Invid(dziecko))
            for child in childrens:
                populacja.append(child)
            ############################################
            #                 MUTACJA
            for inv in populacja:
                if random.random() < mutation:
                    inv.mutation()
                inv.calculate_distance(self.dist_matrix)
                if self.min > inv.distance:
                    self.min = inv.distance
                    self.min_ciag = inv.param_values
            ############################################
            #           SELEKCJA & REDUKCJA
            # posortuj według dystansu
            # wyrzuć najgorszych
            populacja.sort(reverse=True)
            for _ in range(len(childrens)):
                populacja.pop(0)
            ############################################
            liczba_pokolen -= 1

    def plot_result(self):
        print(self.min)
        plt.figure()
        for point in self.c_dist:
            plt.plot(point[0], point[1], 'ko')
        for i in range(len(self.min_ciag)-1):
            x = [self.c_dist[self.min_ciag[i]][0], self.c_dist[self.min_ciag[i+1]][0]]
            y = [self.c_dist[self.min_ciag[i]][1], self.c_dist[self.min_ciag[i + 1]][1]]
            plt.plot(x, y, "r-")
        x = [self.c_dist[self.min_ciag[len(self.min_ciag)-1]][0], self.c_dist[self.min_ciag[0]][0]]
        y = [self.c_dist[self.min_ciag[len(self.min_ciag)-1]][1], self.c_dist[self.min_ciag[0]][1]]
        plt.plot(x, y, "r-")
        plt.show()


if __name__ == "__main__":
    gen = Genetic("data\\city_names.txt", "data\\city_xy.txt")
    gen.start_algorithm(100, 5000)
    gen.plot_result()

