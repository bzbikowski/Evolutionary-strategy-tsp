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
import matplotlib.pyplot as plt
from collections import deque
from pop import Invid


class Genetic:
    def __init__(self, path_names, path_xy):
        """
        :param path_names: ścieżka do pliku tekstowego zawierająca nazwy kolejnych miast
        :param path_xy: ścieżka do pliku z położeniami miast
        """
        blocked = [[1, 2]]
        self.starting_generations = 0
        self.best_results = []
        self.c_names = []
        self.c_dist = []
        self.dist_matrix = []
        self.time_matrix = []
        self.cost_matrix = []
        self.refactor_data(path_names, path_xy)
        self.calc_dist_matrix(blocked)

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
        self.time_matrix = np.zeros((22, 22))
        # macierz kosztu po drogach
        # todo stworzyć sztuczną macierz w pliku txt z kosztem podróży po drogach(autostrada...)
        self.cost_matrix = np.zeros((22, 22))

    def calc_dist(self, xx, yy):
        """
        Na podstawie dwóch punktów policz ich odległość Euklidesową

        :param xx: współrzędne 1. punktu
        :param yy: współrzędne 2. punktu

        :return: rzeczywisty dystans na mapie pomiędzy dwoma miastami
        """
        return ((xx[0] - yy[0]) ** 2 + (xx[1] - yy[1]) ** 2) ** (1 / 2)

    def calc_dist_matrix(self, blocked):
        """
        Wylicz odległości pomiędzy miastami, z uwzględnieniem warunku, że nie wszystkie drogi są przejezdne

        :param blocked: wektor wybranych nieprzejezdnych dróg
        """
        # tablica nieprzejezdnych dróg, możemy dowolnie modyfikować
        self.dist_matrix = np.zeros((len(self.c_dist), len(self.c_dist)))
        for ind1, item1 in enumerate(self.c_dist):
            for ind2, item2 in enumerate(self.c_dist):
                if ind1 == ind2:
                    self.dist_matrix[ind1][ind2] = 0
                else:
                    self.dist_matrix[ind1][ind2] = self.calc_dist(item1, item2)
        for path in blocked:
            self.dist_matrix[path[0]][path[1]] = 9999999
            self.dist_matrix[path[1]][path[0]] = 9999999
        # self.save_dist_matrix("data//wg22_dist.txt")

    def save_dist_matrix(self, pathname):
        np.savetxt(pathname, self.dist_matrix)

    def start_algorithm(self, start_pop=10, no_of_gen=1000, mutation=0.5, no_of_parent=3):
        """
        strategia ewolucyjna uwzględniająca(w jakimś stopniu) położenie miast, czas podróży oraz koszty

        :param no_of_parent: ile osobników wynierzemy do krzyżowania aby wyznaczyć jednego potomka
        :param mutation: prawdopodobieństwo wystąpienia mutacji
        :param start_pop: ilość osobników w każdym pokoleniu, nasze µ
        :param no_of_gen: maksymalna ilość pokoleń w algorytmie
        """
        self.starting_generations = no_of_gen
        liczba_osobnikow = start_pop
        liczba_pokolen = no_of_gen
        populacja = []
        lenght = len(self.c_dist)
        self.min = 999999999
        self.min_ciag = None
        # inicjacja populacji
        for i in range(liczba_osobnikow):
            populacja.append(Invid())
            populacja[i].generate(len(self.dist_matrix))
            populacja[i].calculate_value(self.dist_matrix, self.time_matrix)
        while liczba_pokolen > 0:
            if liczba_pokolen % 10 == 0:
                print("Pokolenie: {}".format(liczba_pokolen))
            ############################################
            #           KRZYŻOWANIE I MUTACJA
            childrens = self.crossover_OX(populacja, lenght)
            # childrens = self.crossover(populacja, lenght, no_of_parents)
            for child in childrens:
                if random.random() < mutation:
                    child.mutation()
                child.calculate_value(self.dist_matrix, self.time_matrix)
                populacja.append(child)
            ############################################
            for inv in populacja:
                if self.min > inv.value:
                    self.min = inv.value
                    self.min_ciag = inv.param_values
            ############################################
            #               SELEKCJA
            populacja.sort(reverse=True)
            for _ in range(len(childrens)):
                populacja.pop(0)
            self.best_results.append(self.min)
            liczba_pokolen -= 1

    def crossover(self, populacja, lenght, no_of_parents=5, multiply=4):
        """
        krzyżowanie rodziców w celu wyznaczenia potomków
        NARAZIE NIE UŻYWANY
        :param multiply: ile razy więcej potomków musimy wyznaczyć
        :param populacja: aktualna populacja osobników
        :param lenght: ilość rozpatrywanych miast
        :param no_of_parents: z ilu rodziców będzie składał się potomek
        """
        # todo zastanowić się nad krzyżowaniem, nie uwzględnia innych parametrów, tylko odległość
        # może PMX albo OX?
        start = None
        childrens = []
        pop_lenght = len(populacja)
        pop_nums = range(0, pop_lenght)
        for _ in range(pop_lenght * multiply):
            dziecko = []
            nums = random.sample(pop_nums, k=no_of_parents)
            krzyzowanie = [populacja[nums[i]] for i in range(len(nums))]
            # wyznacz jednego losowego rodzica
            ruletka = [val for val in np.arange(float(1 / no_of_parents), 1, float(1 / no_of_parents))]
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
                for v in range(0, int(len(values) / 2)):
                    neigh.append(krzyzowanie[v].param_values[values[ind]])  # min
                    neigh.append(krzyzowanie[v].param_values[values[ind + 1]])  # max
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

    def crossover_OX(self, populacja, lenght, multiply=4):
        """
        krzyżowanie rodziców w celu wyznaczenia potomkóm (metoda OX)
        
        :param multiply: ile razy więcej potomków musimy wyznaczyć
        :param populacja: aktualna populacja osobników
        :param lenght: ilość rozpatrywanych miast
        :param no_of_parents: z ilu rodziców będzie składał się potomek
        """
        childrens = []
        pop_lenght = len(populacja)
        pop_nums = range(0, pop_lenght)
        for _ in range(int(pop_lenght * multiply / 2)):
            nums = random.sample(pop_nums, k=2)
            krzyzowanie = [populacja[nums[i]] for i in range(len(nums))]
            random_nrs = sorted(random.sample(range(1, lenght - 1), k=2))
            first_middle = krzyzowanie[0].param_values[random_nrs[0]:random_nrs[1]]
            second_middle = krzyzowanie[1].param_values[random_nrs[0]:random_nrs[1]]
            dziecko1 = np.copy(first_middle)
            dziecko2 = np.copy(second_middle)
            for i in range(lenght):
                current_index = (random_nrs[1] + i) % lenght
                value1 = krzyzowanie[1].param_values[current_index]
                value2 = krzyzowanie[0].param_values[current_index]
                if value1 not in first_middle:
                    dziecko1 = np.append(dziecko1, value1)
                if value2 not in second_middle:
                    dziecko2 = np.append(dziecko2, value2)
            dziecko1 = deque(dziecko1)
            dziecko2 = deque(dziecko2)
            dziecko1.rotate(random_nrs[0])
            dziecko2.rotate(random_nrs[0])
            childrens.append(Invid(list(dziecko1)))
            childrens.append(Invid(list(dziecko2)))
        return childrens

    def plot_result(self):
        """
        narysuj na ekranie wykresy dot.:
        a) najlepsza znaleziona droga
        b) minimalna znaleziona odległość na przestrzeni pokoleń
        """
        fig1 = plt.figure()
        ax1 = fig1.add_subplot('111')
        ax1.set_title(str(self.min))
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
        ax2.plot(range(self.starting_generations), self.best_results, '-k')
        fig2.show()

    def plot_cities(self):
        """
        narysuj mapę poglądową problemu
        """
        fig = plt.figure()
        ax = fig.add_subplot("111")
        for i in range(len(self.c_dist)):
            ax.plot(self.c_dist[i][0], self.c_dist[i][1], 'ro')
            ax.text(self.c_dist[i][0] - 10, self.c_dist[i][1] - 5, "{0}. {1}".format(i + 1, self.c_names[i]))
        fig.show()


if __name__ == "__main__":
    gen2 = Genetic("data\\wg22_name.txt", "data\\wg22_xy.txt")
    gen2.plot_cities()
    gen2.start_algorithm(100, 200, 0.05, 2)
    gen2.plot_result()
