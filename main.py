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
from pop import Invid


def refactor_name_data():
    """
    Wczytywanie z pliku nazw miast, które wykorzystujemy w tym projekcie

    :return: city_names - lista nazwm miast
    """
    city_names = []
    city_states = []
    with open("data//city_names.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(", ")
            if parts[0] == '\n':
                break
            city_names.append(parts[0])
            city_states.append(parts[1][:-1])
    return city_names, city_states


def refactor_dist_data():
    """
    Wczytaj z pliku współrzędne każdego miasta na mapie geograficnzej

    :return: data - macierz dwukolumnowa, która dla każdego miasta przechowuje punkt współrzędnych x i y
    """
    data = np.loadtxt("data//city_xy.txt")
    return data


def calc_dist(xx, yy):
    """
    Na podstawie dwóch punktów policz ich odległość Euklidesową

    :param xx: współrzędne 1. punktu
    :param yy: współrzędne 2. punktu

    :return: rzeczywisty dystans na mapie pomiędzy dwoma miastami
    """
    return ((xx[0]-yy[0])**2+(xx[1]-yy[1])**2)**(1/2)


def calc_dist_matrix(distance, break_param):
    """
    Wylicz odległości pomiędzy miastami, z uwzględnieniem warunku, że nie wszystkie drogi są przejezdne

    :param distance: macierz zawierająca współrzędne miast
    :param break_param: współczynnik, który oznacza jak często nie będzie danej drogi pomiędzy miastami

    :return: dist_matrix - macierz odległości każdego miasta z każdym miastem
    """
    dist_matrix = np.zeros((len(distance), len(distance)))
    for ind1, item1 in enumerate(distance):
        for ind2, item2 in enumerate(distance):
            if ind1 == ind2:
                dist_matrix[ind1][ind2] = 0
            else:
                val = random.random()
                if val < break_param:
                    dist_matrix[ind1][ind2] = 99999999999999
                else:
                    dist_matrix[ind1][ind2] = calc_dist(item1, item2)
    return dist_matrix


def evolutionary_strategy(matrix):
    """
    strategia ewolucyjna narazie tylko dla odległości pomiędzy miastami

    :param matrix:

    :return:
    """
    liczba_osobnikow = 10
    liczba_pokolen = 5000
    populacja = []
    for i in range(liczba_osobnikow):
        populacja.append(Invid())
        populacja[i].generate(len(matrix))
        populacja[i].calculate_distance(matrix)
    while liczba_pokolen > 0:
        ############################################
        #               KRZYŻOWANIE
        random_starting_point = random.randrange(48)
        ############################################
        #                 MUTACJA
        for inv in populacja:
            inv.mutation()
        ############################################
        #           SELEKCJA & REDUKCJA
        # posortuj według dystansu
        # wypierdol najgorszych, aby zostało 10 osobników
        ############################################
        liczba_osobnikow -= 1

def plot_result():
    plt.figure()
    for point in c_dist:
        plt.plot(point[0], point[1], 'ko')
    # potem plotuj optymalne krawędzie
    plt.show()


if __name__ == "__main__":
    # zrobić słownik?
    c_names, c_states = refactor_name_data()
    # starting_point = "Santa Fe"
    c_dist = refactor_dist_data()
    m_dist = calc_dist_matrix(c_dist, 0)
    evolutionary_strategy(m_dist)
    plot_result()

