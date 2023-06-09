import math
import random
from abc import ABC
from typing import List

from src.individual import Individual


def temperature(t0: float, tc: float, k: float, t: int) -> float:
    return tc + (t0 - tc) * math.exp(-k * t)


def expected_value(fitness: float, temp: float, avg: float) -> float:
    return math.exp(fitness / temp) / avg


class SelectionMethod(ABC):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        pass


class EliteSelection(SelectionMethod):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        winners = []

        length = len(population)
        if length == 0:
            return winners

        population.sort(key=lambda ind: ind.fitness(), reverse=True)

        for i, individual in enumerate(population):
            n = math.ceil((k - i) / length)
            for j in range(n):
                winners.append(individual)

        return winners


def do_roulette(population: List[Individual], length: int, k: int, fitness_list: List[float]):
    winners = []

    fitness_sum = sum(fitness_list)

    for i in range(k):
        r = random.random()
        accumulated_fitness = 0
        for j in range(length):
            relative_fitness = fitness_list[j] / fitness_sum
            if accumulated_fitness < r <= accumulated_fitness + relative_fitness:
                winners.append(population[j])
                break
            accumulated_fitness += relative_fitness

    return winners


class RouletteWheelSelection(SelectionMethod):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        length = len(population)
        if length == 0:
            return []

        individual_fitness_list = [ind.fitness() for ind in population]
        return do_roulette(population, length, k, individual_fitness_list)


class UniversalSelection(SelectionMethod):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        winners = []

        length = len(population)
        if length == 0:
            return winners

        fitness_list = [ind.fitness() for ind in population]
        fitness_sum = sum(fitness_list)

        r = random.random()
        for i in range(k):
            ri = (r + i) / k
            accumulated_fitness = 0
            for j in range(length):
                relative_fitness = fitness_list[j] / fitness_sum
                if accumulated_fitness < ri <= accumulated_fitness + relative_fitness:
                    winners.append(population[j])
                    break
                accumulated_fitness += relative_fitness

        return winners


class RankSelection(RouletteWheelSelection):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        length = len(population)
        if length == 0:
            return []

        population.sort(key=lambda ind: ind.fitness(), reverse=True)
        individual_fitness_list = [(length - (idx + 1)) / length for idx, ind in enumerate(population)]

        return do_roulette(population, length, k, individual_fitness_list)


class EntropicBoltzmannSelection(SelectionMethod):
    def __init__(self, t0: float, tc: float, k: float):
        self._k = k
        self._t0 = t0
        self._tc = tc

    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        length = len(population)
        if length == 0:
            return []

        temp = temperature(self._t0, self._tc, self._k, k)
        pseudo_fitness_list = [math.exp(ind.fitness() / temp) for ind in population]
        avg_population = sum(pseudo_fitness_list) / len(pseudo_fitness_list)
        pseudo_fitness_list = [fitness / avg_population for fitness in pseudo_fitness_list]

        return do_roulette(population, length, k, pseudo_fitness_list)


class DeterministicTournamentSelection(SelectionMethod):
    def __init__(self, m: int):
        self._m = m

    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        winners = []

        length = len(population)
        if len(population) == 0:
            return winners

        for i in range(k):
            best = population[random.randint(0, length - 1)]
            best_fitness = best.fitness()
            for j in range(1, self._m):
                chosen = population[random.randint(0, length - 1)]
                aux_fitness = chosen.fitness()
                if best_fitness < aux_fitness:
                    best = chosen
                    best_fitness = aux_fitness
            winners.append(best)

        return winners


class ProbabilisticTournamentSelection(SelectionMethod):
    def get_winners(self, population: List[Individual], k: int) \
            -> List[Individual]:
        winners = []

        length = len(population)
        if length == 0:
            return winners

        threshold = random.uniform(0.5, 1)
        length = len(population)

        for i in range(k):
            first = population[random.randint(0, length - 1)]
            second = population[random.randint(0, length - 1)]
            first_fitness = first.fitness()
            second_fitness = second.fitness()

            best = first if first_fitness > second_fitness else second
            worst = second if first_fitness > second_fitness else first

            r = random.uniform(0, 1)

            if r < threshold:
                winners.append(best)
            else:
                winners.append(worst)

        return winners
