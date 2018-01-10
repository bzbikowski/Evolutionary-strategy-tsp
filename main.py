import numpy as np
import random
import matplotlib.pyplot as plt
import time
import os
from pop import Invid


class Genetic:
    """
    Główna klasa programu
    """
    def __init__(self, path_names, path_xy):
        """
        :param path_names: ścieżka do pliku tekstowego zawierająca nazwy kolejnych miast
        :type path_names: string
        :param path_xy: ścieżka do pliku z położeniami miast
        :type path_xy: string
        """
        self.best_results = []
        self.c_names = {}
        self.c_dist = []
        self.dist_matrix = []
        self.time_matrix = []
        self.cost_matrix = []
        self.start_time = None
        self.best_time = None
        self.best_gen = None
        self.load_data(path_names, path_xy)
        # lista zablokowanych dróg
        blocked = [["Koeln", "Saarbruecken"]]
        self.calc_dist_matrix(blocked)

    def load_data(self, names_path, xy_path):
        """
        Wczytywanie z pliku współrzędne każdego miasta oraaz ich nazw miast, które wykorzystujemy w tym projekcie

        :param names_path: ścieżka do pliku tekstowego zawierająca nazwy kolejnych miast
        :type names_path: string
        :param xy_path: ścieżka do pliku z położeniami miast
        :type xy_path: string
        """
        with open(names_path, 'r') as file:
            index = 0
            lines = file.read().splitlines()
            for line in lines:
                self.c_names[line] = index
                index += 1
        self.c_dist = np.loadtxt(xy_path)
        self.time_matrix = np.zeros((15, 15))
        self.cost_matrix = np.zeros((15, 15))

    def calc_dist(self, xx, yy):
        """
        Na podstawie dwóch punktów policz ich odległość Euklidesową

        :param xx: współrzędne 1. punktu
        :type xx: list(shape=[2])
        :param yy: współrzędne 2. punktu
        :type yy: list(shape=[2])

        :return: rzeczywisty dystans na mapie pomiędzy dwoma miastami
        :type return: float
        """
        return ((xx[0] - yy[0]) ** 2 + (xx[1] - yy[1]) ** 2) ** (1 / 2)

    def create_time_and_cost_matrixes(self):
        for i in range(len(self.c_dist)):
            for j in range(i, len(self.c_dist)):
                traffic = random.random()
                autostrada = random.random()
                if traffic < 0.7:
                    self.time_matrix[i][j] = self.time_matrix[j][i] = self.dist_matrix[i][j] * 2
                else:
                    self.time_matrix[i][j] = self.time_matrix[j][i] = self.dist_matrix[i][j] * 5
                if autostrada < 0.8:
                    self.cost_matrix[i][j] = self.cost_matrix[j][i] = self.time_matrix[i][j] * 4
                else:
                    self.cost_matrix[i][j] = self.cost_matrix[j][i] = self.time_matrix[i][j] * 6

    def calc_dist_matrix(self, blocked):
        """
        Wylicz odległości pomiędzy miastami oraz uwzględnienienie warunku, że nie wszytstkie drogi są przejezdne

        :param blocked: wektor wybranych nieprzejezdnych dróg
        :type blocked: list
        """
        self.dist_matrix = np.zeros((len(self.c_dist), len(self.c_dist)))
        for ind1, item1 in enumerate(self.c_dist):
            for ind2, item2 in enumerate(self.c_dist):
                if ind1 == ind2:
                    self.dist_matrix[ind1][ind2] = 0
                else:
                    self.dist_matrix[ind1][ind2] = self.calc_dist(item1, item2)
        if os.path.isfile("data//wg22_time.txt") and os.path.isfile("data//wg22_cost.txt"):
            self.time_matrix = np.loadtxt("data//wg22_time.txt")
            self.cost_matrix = np.loadtxt("data//wg22_cost.txt")
        else:
            self.create_time_and_cost_matrixes()
            self.save_matrixes()
        for path in blocked:
            city1 = self.c_names[path[0]]
            city2 = self.c_names[path[1]]
            self.time_matrix[city1][city2] = 9999999
            self.time_matrix[city2][city1] = 9999999

    def save_matrixes(self):
        """
        Zapis do pliku wyliczonej macierzy odległości pomiędzy każdym miastem

        :param pathname: ścieżka do zapisu pliku tekstowego
        :type pathname: string
        """
        np.savetxt("data//wg22_dist.txt", self.dist_matrix)
        np.savetxt("data//wg22_time.txt", self.time_matrix)
        np.savetxt("data//wg22_cost.txt", self.cost_matrix)

    def start_algorithm(self, start_pop=10, no_of_gen=1000, mutation=1):
        """
        Algotyrtm strategii ewolucyjnej (µ+λ).

        :param int start_pop: początkowa ilość osobników w każdym pokoleniu
        :param int no_of_gen: maksymalna ilość pokoleń w algorytmie
        :param float mutation: prawdopodobieństwo wystąpienia mutacji
        """
        liczba_pokolen = no_of_gen
        liczba_osobnikow = start_pop
        populacja = []
        self.min = 999999999
        self.min_ciag = None
        self.start_time = time.time()
        # inicjacja populacji
        for i in range(liczba_osobnikow):
            populacja.append(Invid())
            populacja[i].generate(len(self.dist_matrix))
            populacja[i].calculate_value(self.dist_matrix, self.time_matrix, self.cost_matrix)
        while liczba_pokolen > 0:
            if liczba_pokolen % 10 == 0:
                print("Pokolenie: {}".format(liczba_pokolen))
            ############################################
            #           KRZYŻOWANIE I MUTACJA
            childrens = self.crossover_arithmetic2(populacja)
            for child in childrens:
                if random.random() < mutation:
                    child.mutation()
                child.calculate_value(self.dist_matrix, self.time_matrix, self.cost_matrix)
                populacja.append(child)
            ############################################
            #           ZNAJDŹ LEPSZEGO OSOBNIKA
            for inv in populacja:
                if self.min > inv.value:
                    self.min = inv.value
                    self.min_ciag = inv.track
                    self.best_time = time.time()
                    self.best_gen = no_of_gen - liczba_pokolen
            ############################################
            #               SELEKCJA
            populacja.sort()
            populacja = populacja[:liczba_osobnikow]
            self.best_results.append(self.min)
            liczba_pokolen -= 1

    def crossover_arithmetic(self, populacja, multiply=4):
        """
        Operacja krzyżowania pośredniego

        :param list populacja: obecna populacja w pokoleniu
        :param int multiply: wyznacznik ile razy więcej dzieci ma powstać w stosunku do liczby populacji
        :return: pula potomków
        :type return: list
        """
        childrens = []
        pop_lenght = len(populacja)
        pop_nums = range(0, pop_lenght)
        for _ in range(pop_lenght * multiply):
            nums = random.sample(pop_nums, k=2)
            krzyzowanie = [populacja[nums[i]] for i in range(len(nums))]
            new_param = np.divide(np.add(krzyzowanie[0].param_values, krzyzowanie[1].param_values), 2)
            new_odch = np.divide(np.add(krzyzowanie[0].odchylenia, krzyzowanie[1].odchylenia), 2)
            childrens.append(Invid([list(new_param), list(new_odch)]))
        return childrens

    def crossover_arithmetic2(self, populacja, multiply=4):
        """
        Operacja krzyżowania arytmetycznego

        :param list populacja: obecna populacja w pokoleniu
        :param int multiply: wyznacznik ile razy więcej dzieci ma powstać w stosunku do liczby populacji
        :return: pula potomków
        :type return: list
        """
        childrens = []
        pop_lenght = len(populacja)
        pop_nums = range(0, pop_lenght)
        for _ in range(int(pop_lenght * multiply / 2)):
            nums = random.sample(pop_nums, k=2)
            krzyzowanie = [populacja[nums[i]] for i in range(len(nums))]
            point = random.randint(0, 15)
            new_param1 = krzyzowanie[0].param_values[:point] + krzyzowanie[1].param_values[point:]
            new_param2 = krzyzowanie[1].param_values[:point] + krzyzowanie[0].param_values[point:]
            new_odch1 = krzyzowanie[0].odchylenia[:point] + krzyzowanie[1].odchylenia[point:]
            new_odch2 = krzyzowanie[1].odchylenia[:point] + krzyzowanie[0].odchylenia[point:]
            childrens.append(Invid([new_param1, new_odch1]))
            childrens.append(Invid([new_param2, new_odch2]))
        return childrens

    def plot_result(self):
        """
        Narysuj na ekranie wykresy dot.:\n
        a) najlepsza znaleziona droga
        b) minimalna znaleziona odległość na przestrzeni pokoleń
        """
        print("\nNajlepsze znalezione rozwiązanie: {}".format(self.min))
        print("Znaleziony w {} pokoleniu, potrzebny czas: {}s".format(self.best_gen, self.best_time - self.start_time))
        print("Całkowity potrzebny czas: {}s".format(time.time() - self.start_time))
        fig1 = plt.figure()
        ax1 = fig1.add_subplot('111')
        ax1.set_title("Najlepsze rozwiązanie")
        ax1.set_xlabel("Współrzędne X [km]")
        ax1.set_ylabel("Współrzędne Y [km]")
        for point in self.c_dist:
            ax1.plot(point[0], point[1], 'ko')
        for i in range(len(self.min_ciag) - 1):
            x = [self.c_dist[self.min_ciag[i]][0], self.c_dist[self.min_ciag[i + 1]][0]]
            y = [self.c_dist[self.min_ciag[i]][1], self.c_dist[self.min_ciag[i + 1]][1]]
            ax1.plot(x, y, "r-")
        x = [self.c_dist[self.min_ciag[len(self.min_ciag) - 1]][0], self.c_dist[self.min_ciag[0]][0]]
        y = [self.c_dist[self.min_ciag[len(self.min_ciag) - 1]][1], self.c_dist[self.min_ciag[0]][1]]
        ax1.plot(x, y, "r-")
        fig1.show()

        fig2 = plt.figure()
        ax2 = fig2.add_subplot('111')
        ax2.set_title("Wykres najlepszego rozwiązania w ciągu pokoleń")
        ax2.set_xlabel("Pokolenie")
        ax2.set_ylabel("Najlepsza wartość")
        ax2.plot(range(len(self.best_results)), self.best_results, '-k')
        fig2.show()

    def plot_cities(self):
        """
        Narysuj mapę poglądową problemu
        """
        list_of_towns = list(self.c_names.keys())
        fig = plt.figure()
        ax = fig.add_subplot("111")
        ax.set_title("Mapa omawianych miast")
        ax.set_xlabel("Współrzędne X [km]")
        ax.set_ylabel("Współrzędne Y [km]")
        for i in range(len(self.c_dist)):
            ax.plot(self.c_dist[i][0], self.c_dist[i][1], 'ro')
            ax.text(self.c_dist[i][0] - 10, self.c_dist[i][1] - 10, "{0}. {1}".format(i + 1, list_of_towns[i]))
        fig.show()


if __name__ == "__main__":
    gen2 = Genetic("data\\wg22_name.txt", "data\\wg22_xy.txt")
    gen2.plot_cities()
    gen2.start_algorithm(200, 200, 1)
    gen2.plot_result()
    input("Wciśnięcie klawisza kończy działanie programu...")
