from axelrod.action import Action
from axelrod.player import Player

C, D = Action.C, Action.D


class Detective(Player):
    """
    A player who chooses Cooperate, Defect, Cooperate, Cooperate
    on the first four rounds.

    After that, as long as the opponent cooperates, keep defecting.
    If the opponent ever retaliates with a 

    Names

    - Detective: [Case17]

    """

    name = 'Detective'
    classifier = {
        'memory_depth': 1,
        'stochastic': False,
        'makes_use_of': set(),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def strategy(self, opponent: Player) -> Action:
        if len(self.history) == 0:
            return C
        if len(self.history) == 1:
            return D
        if len(self.history) == 2:
            return C
        if len(self.history) == 3:
            return C
        if opponent.defections:
            if opponent.history[-1] == D:
                return D
            return C
        else:
            return D
