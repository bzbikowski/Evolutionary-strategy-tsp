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
        """

        :param path_names:
        :param path_xy:
        """
        self.c_names = []
        self.c_dist = []
        self.dist_matrix = []
        self.time_matrix = []
        self.cost_matrix = []
        self.refactor_data(path_names, path_xy)
        self.calc_dist_matrix()

    def refactor_data(self, names_path, xy_path):
        """
        Wczytywanie z pliku współrzędne każdego miasta oraaz ich nazw miast, które wykorzystujemy w tym projekcie

        :return: c_names - lista nazwm miast
                 c_dist - macierz dwukolumnowa, która dla każdego miasta przechowuje punkt współrzędnych x i y
        """
        with open(names_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split(", ")
                if parts[0] == '\n':
                    break
                self.c_names.append(parts[0])
        self.c_dist = np.loadtxt(xy_path)
        # macierz czasu podróży
        # todo stworzyć sztuczną macierz w pliku txt z czasem podróży(zatłoczenie drogi...)
        self.time_matrix = np.zeros(22, 22)
        # macierz kosztu po drogach
        # todo stworzyć sztuczną macierz w pliku txt z kosztem podróży po drogach(autostrada...)
        self.cost_matrix = np.zeros(22, 22)

    def calc_dist(self, xx, yy):
        """
        Na podstawie dwóch punktów policz ich odległość Euklidesową

        :param xx: współrzędne 1. punktu
        :param yy: współrzędne 2. punktu

        :return: rzeczywisty dystans na mapie pomiędzy dwoma miastami
        """
        return ((xx[0]-yy[0])**2+(xx[1]-yy[1])**2)**(1/2)

    def calc_dist_matrix(self, break_param=0.001):
        """
        Wylicz odległości pomiędzy miastami, z uwzględnieniem warunku, że nie wszystkie drogi są przejezdne

        :param distance: macierz zawierająca współrzędne miast
        :param break_param: współczynnik, który oznacza jak często nie będzie danej drogi pomiędzy miastami

        :return: dist_matrix - macierz odległości każdego miasta z każdym miastem
        """
        # todo znaleźć jakieś lepsze rozwiązanie nieprzejezdnych dróg
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

    def start_algorithm(self, start_pop=10, no_of_gen=1000, mutation=0.05, no_of_parent=3):
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
            childrens = self.crossover(populacja, lenght, no_of_parent)
            for child in childrens:
                populacja.append(child)
            ############################################
            #                 MUTACJA
            for inv in populacja:
                if random.random() < mutation:
                    inv.mutation()
                inv.calculate_value(self.dist_matrix, self.time_matrix)
                if self.min > inv.value:
                    self.min = inv.value
                    self.min_ciag = inv.param_values
            ############################################
            #               SELEKCJA
            populacja.sort(reverse=True)
            for _ in range(len(childrens)):
                populacja.pop(0)
            liczba_pokolen -= 1

    def crossover(self, populacja, lenght, no_of_parents=5):
        """

        :param populacja:
        :param lenght:
        :param no_of_parents:
        :return:
        """
        start = None
        childrens = []
        copy_pop = np.copy(populacja)
        np.random.shuffle(copy_pop)
        for _ in range(math.floor(len(populacja) / no_of_parents)):
            dziecko = []
            nums = random.sample(range(0, len(copy_pop)), k=no_of_parents)
            krzyzowanie = [copy_pop[nums[i]] for i in range(len(nums))]
            copy_pop = np.delete(copy_pop, nums)
            # wyznacz jednego losowego rodzica
            ruletka = [val for val in np.arange(float(1/no_of_parents), 1, float(1/no_of_parents))]
            ruletka.append(1)
            val_rand = random.random()
            for j in range(len(ruletka)):
                if val_rand < ruletka[j]:
                    start = krzyzowanie[j]
                    break
            random_city = random.randint(0, lenght - 1)
            param = start.param_values[random_city]
            # dodaj losowe miasto z jego ścieżki jako pierwszy element
            dziecko.append(param)
            for i in range(lenght - 1):
                vals = []
                for j in range(len(krzyzowanie)):
                    vals.append(krzyzowanie[j].param_values.index(param))
                values = []
                for value in vals:
                    min = value - 1
                    if min < 0:
                        min = lenght - 1
                    values.append(min)
                    max = value + 1
                    if max > lenght - 1:
                        max = 0
                    values.append(max)
                neigh = []
                ind = 0
                for v in range(0, int(len(values)/2)):
                    neigh.append(krzyzowanie[v].param_values[values[ind]])  # min
                    neigh.append(krzyzowanie[v].param_values[values[ind+1]])  # max
                    ind += 2
                dist_vector = [self.dist_matrix[dziecko[i]][j] for j in neigh]
                values, dist_vector = (list(x) for x in
                                       zip(*sorted(zip(values, dist_vector), key=lambda pair: pair[1])))
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
        return childrens

    def plot_result(self):
        """

        :return:
        """
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
    # gen1 = Genetic("data\\city_names.txt", "data\\city_xy.txt")
    # gen1.start_algorithm(500, 10000)
    # gen1.plot_result()
    gen2 = Genetic("data\\wg22_name.txt", "data\\wg22_xy.txt")
    gen2.start_algorithm(500, 10000, 0.05, 4)
    gen2.plot_result()

# 35832.9229342
# 1128.47964321