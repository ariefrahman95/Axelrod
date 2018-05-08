"""Implementation of the Case tournament process on Graphs."""

from collections import Counter
import random

import matplotlib.pyplot as plt
import numpy as np

from heapq import nsmallest
from axelrod import DEFAULT_TURNS, Player, Game
from .deterministic_cache import DeterministicCache
from .graph import complete_graph, Graph
from .match import Match
from .random_ import randrange

from typing import List, Tuple, Set

class CaseProcess(object):
    def __init__(self, players: List[Player], turns: int = DEFAULT_TURNS,
                 maximum_round: int = 10, noise: float = 0,
                 noise_bias: bool = False, prob_end: float = None,
                 replace_amount: int = 1, game: Game = None,
                 deterministic_cache: DeterministicCache = None,
                 interaction_graph: Graph = None,
                 reproduction_graph: Graph = None) -> None:
        """
        An agent based Case process class. In each round, each player plays a
        Match with each other player. Players are assigned a fitness score by
        their total score from all matches in the round. The best player will
        be cloned n times. The clones replace n players with the lowest fitness.

        If the mutation_rate is 0, the population will eventually fixate on
        exactly one player type. In this case a StopIteration exception is
        raised and the play stops. If the mutation_rate is not zero, then the
        process will iterate indefinitely, so mp.play() will never exit, and
        you should use the class as an iterator instead.

        It is possible to pass interaction graphs and reproduction graphs to the
        Case process. In this case, in each round, each player plays a
        Match with each neighboring player according to the interaction graph.
        Players are assigned a fitness score by their total score from all
        matches in the round. A player is chosen to reproduce proportionally to
        fitness, possibly mutated, and is cloned. The clone replaces a randomly
        chosen neighboring player according to the reproduction graph.

        Parameters
        ----------
        players
        turns:
            The number of turns in each pairwise interaction
        noise:
            The background noise, if any. Randomly flips plays with probability
            `noise`.
        noise_bias :
            If True, only flips cooperate plays into defects
        prob_end :
            The probability of a given turn ending a match
        replace_amount:
            The amount of player(s) to replace at the end of each round
        deterministic_cache:
            A optional prebuilt deterministic cache
        mode:
            Birth-Death (bd) or Death-Birth (db)
        interaction_graph: Axelrod.graph.Graph
            The graph in which the replicators are arranged
        reproduction_graph: Axelrod.graph.Graph
            The reproduction graph, set equal to the interaction graph if not
            given
        """
        self.turns = turns
        self.maximum_round = maximum_round
        self.current_round = 0
        self.current_scores = [] # type: List
        self.game = game
        self.noise = noise
        self.noise_bias = noise_bias
        self.prob_end = prob_end
        self.replace_amount = replace_amount
        self.initial_players = players  # save initial population
        self.players = []  # type: List
        assert self.replace_amount < len(players)
        self.populations = []  # type: List
        self.set_players()
        self.score_history = []  # type: List
        self.winning_strategy_name = None  # type: str
        assert (noise >= 0) and (noise <= 1)
        if deterministic_cache is not None:
            self.deterministic_cache = deterministic_cache
        else:
            self.deterministic_cache = DeterministicCache()

        interaction_graph = complete_graph(len(players), loops=False)
        reproduction_graph = Graph(interaction_graph.edges(),
                                    directed=interaction_graph.directed)
        reproduction_graph.add_loops()
        # Check equal vertices
        v1 = interaction_graph.vertices()
        v2 = reproduction_graph.vertices()
        assert list(v1) == list(v2)
        self.interaction_graph = interaction_graph
        self.reproduction_graph = reproduction_graph
        # Map players to graph vertices
        self.locations = sorted(interaction_graph.vertices())
        self.index = dict(zip(sorted(interaction_graph.vertices()),
                              range(len(players))))

    def set_players(self) -> None:
        """Copy the initial players into the first population."""
        self.players = []
        for player in self.initial_players:
            player.reset()
            self.players.append(player)
        self.populations = [self.population_distribution()]

    def death(self) -> (int, float):
        """
        Selects the players with the lowest fitness to be removed.

        Parameters
        ----------
        index:
            List of the index of players to be removed
        """
        lowest_scorers = [ idx for idx, score in enumerate(self.current_scores) if score == np.min(self.current_scores) ]
        lowest_scorer = random.choice(lowest_scorers)
        lowest_score = self.current_scores[lowest_scorer]
        return lowest_scorer, lowest_score

    def birth(self, index: int = None) -> (int, float):
        """The birth event.

        Parameters
        ----------
        index:
            The index of the player to be copied
        """
        highest_scorers = [ idx for idx, score in enumerate(self.current_scores) if score == np.max(self.current_scores) ]
        highest_scorer = random.choice(highest_scorers)
        highest_score = self.current_scores[highest_scorer]
        return (highest_scorer, highest_score)

    def fixation_check(self) -> bool:
        """
        Checks if the population is all of a single type

        Returns
        -------
        Boolean:
            True if fixation has occurred (population all of a single type)
        """
        classes = set(str(p) for p in self.players)
        if len(classes) == 1:
            # Set the winning strategy name variable
            self.winning_strategy_name = str(self.players[0])
            return True
        return False

    def __next__(self) -> object:
        """
        Iterate the population:

        - play the round's matches
        - choose the player with the highest score
        - choose n players to be replaced
        - update the population

        Returns
        -------
        CaseProcess:
            Returns itself with a new population
        """
        
        # Check the exit condition, that all players are of the same type.
        if self.fixation_check() or self.current_round == self.maximum_round:
            raise StopIteration

        print(self.population_distribution())

        # Kill the lowest scorers and replace them with the best player
        self.current_scores = self.score_all()
        high_scorer, high_score = self.birth()
        stop_flag = False

        for _ in range(self.replace_amount):
            low_scorer, low_score = self.death()
            # If the highest scorer has the same score as the lowest,
            # immediately stop the process.
            if low_score == high_score:
                stop_flag = True
                break
            new_player = self.players[high_scorer].clone()
            self.players[low_scorer] = new_player

        self.populations.append(self.population_distribution())
        if stop_flag:
            raise StopIteration
        # Check again for fixation
        self.fixation_check()
        self.current_round += 1
        return self

    def _matchup_indices(self) -> Set[Tuple[int, int]]:
        """
        Generate the matchup pairs.

        Returns
        -------
        indices:
            A set of 2 tuples of matchup pairs: the collection of all players
            who play each other.
        """
        indices = set()  # type: Set
        sources = sorted(self.locations)
        for i, source in enumerate(sources):
            for target in sorted(self.interaction_graph.out_vertices(source)):
                j = self.index[target]
                if (self.players[i] is None) or (self.players[j] is None):
                    continue
                # Prevent duplicate matches
                if ((i, j) in indices) or ((j, i) in indices):
                    continue
                indices.add((i, j))
        return indices

    def score_all(self) -> List:
        """Plays the next round of the process. Every player is paired up
        against every other player and the total scores are recorded.

        Returns
        -------
        scores:
            List of scores for each player
        """
        N = len(self.players)
        scores = [0] * N
        for i, j in self._matchup_indices():
            player1 = self.players[i]
            player2 = self.players[j]
            match = Match((player1, player2),
                          turns=self.turns, prob_end=self.prob_end,
                          noise=self.noise,
                          noise_bias=self.noise_bias,
                          game=self.game,
                          deterministic_cache=self.deterministic_cache)
            match.play()
            match_scores = match.final_score_per_turn()
            scores[i] += match_scores[0]
            scores[j] += match_scores[1]
        self.score_history.append(scores)
        return scores

    def population_distribution(self) -> Counter:
        """Returns the population distribution of the last iteration.

        Returns
        -------
        counter:
            The counts of each strategy in the population of the last iteration
        """
        player_names = [str(player) for player in self.players]
        counter = Counter(player_names)
        return counter

    def __iter__(self) -> object:
        """
        Returns
        -------
        self
        """
        return self

    def reset(self) -> None:
        """Reset the process to replay."""
        self.winning_strategy_name = None
        self.score_history = []
        # Reset all the players
        self.set_players()

    def play(self) -> List[Counter]:
        """
        Play the process out to completion. If played with mutation this will
        not terminate.

        Returns
        -------
         populations:
            Returns a list of all the populations
        """
        print('\nExecuting Case tournament...')
        i = 1
        while True:
            print('Round %d' % i)
            try:
                self.__next__()
            except StopIteration:
                break
            i += 1
        print('Case tournament executed successfully.\n')
        return self.populations

    def __len__(self) -> int:
        """
        Returns
        -------
            The length of the Case process: the number of populations
        """
        return len(self.populations)

    def populations_plot(self, ax=None):
        """
        Create a stackplot of the population distributions at each iteration of
        the Case process.

        Parameters
        ----------------
        ax: matplotlib axis
            Allows the plot to be written to a given matplotlib axis.
            Default is None.

        Returns
        -----------
        A matplotlib axis object

        """
        player_names = self.populations[0].keys()
        if ax is None:
            _, ax = plt.subplots()
        else:
            ax = ax

        plot_data = []
        labels = []
        for name in player_names:
            labels.append(name)
            values = [counter[name] for counter in self.populations]
            plot_data.append(values)
            domain = range(len(values))

        ax.stackplot(domain, plot_data, labels=labels)
        ax.set_title("Case Process Population by Iteration")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Number of Individuals")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
        return ax


class ApproximateCaseProcess(CaseProcess):
    """
    A class to approximate a Case process based
    on a distribution of potential Match outcomes.

    Instead of playing the matches, the result is sampled
    from a dictionary of player tuples to distribution of match outcomes
    """
    def __init__(self, players: List[Player], cached_outcomes: dict) -> None:
        """
        Parameters
        ----------
        players:
        cached_outcomes:
            Mapping tuples of players to instances of the case.Pdf class.
        mutation_rate:
            The rate of mutation. Replicating players are mutated with
            probability `mutation_rate`
        """
        super(ApproximateCaseProcess, self).__init__(
            players, turns=0, noise=0, deterministic_cache=None)
        self.cached_outcomes = cached_outcomes

    def score_all(self) -> List:
        """Plays the next round of the process. Every player is paired up
        against every other player and the total scores are obtained from the
        cached outcomes.

        Returns
        -------
        scores:
            List of scores for each player
        """
        N = len(self.players)
        scores = [0] * N
        for i in range(N):
            for j in range(i + 1, N):
                player_names = tuple([str(self.players[i]),
                                      str(self.players[j])])

                cached_score = self._get_scores_from_cache(player_names)
                scores[i] += cached_score[0]
                scores[j] += cached_score[1]
        self.score_history.append(scores)
        return scores

    def _get_scores_from_cache(self, player_names: Tuple) -> Tuple:
        """
        Retrieve the scores from the players in the cache

        Parameters
        ----------
        player_names:
            The names of the players

        Returns
        -------
        scores:
            The scores of the players in that particular match
        """
        try:
            match_scores = self.cached_outcomes[player_names].sample()
            return match_scores
        except KeyError:  # If players are stored in opposite order
            match_scores = self.cached_outcomes[player_names[::-1]].sample()
            return match_scores[::-1]
