import axelrod as axl
import typing
import sys, inspect
import importlib
import logging
import matplotlib.pyplot as plt

def do_axelrod_tournament(players: list, output_file_name: str,
                          noise: float = 0, noise_bias: bool = False,
                          prob_end: float = 0, seed: int = 0) -> None:
    axl.seed(seed)
    tournament = axl.Tournament(players, noise=noise, noise_bias=noise_bias, prob_end=prob_end)  # Create a tournament
    results = tournament.play()  # Play the tournament
    # print(results.summarise())
    plot = axl.Plot(results)
    plot.boxplot()
    plt.savefig('boxplot_' + output_file_name, format='png')
    plot.winplot()
    plt.savefig('winplot_' + output_file_name, format='png')
    plot.payoff()
    plt.savefig('payoff_' + output_file_name, format='png')
    plt.close('all')

def do_case_tournament(players: list, output_file_name: str,
                       turns: int = axl.DEFAULT_TURNS, prob_end: float = None,
                       maximum_round: int = 20, noise: float = 0,
                       noise_bias: bool = False, replace_amount: int = 1,
                       game: axl.Game = None, seed: int = 0) -> None:
    axl.seed(seed)
    tournament = axl.CaseProcess(players, turns=turns, maximum_round=maximum_round,
        replace_amount=replace_amount, noise=noise, noise_bias=noise_bias, game=game,
        prob_end=prob_end)
    tournament.play()
    tournament.populations_plot()
    plt.savefig(output_file_name, format='png', bbox_inches='tight')
    plt.close()

axl_first_players = [
    axl.TitForTat(),
    axl.TidemanAndChieruzzi(),
    axl.Nydegger(),
    axl.Grofman(),
    axl.Shubik(),
    axl.SteinAndRapoport(),
    axl.Grudger(),
    axl.Davis(),
    axl.RevisedDowning(),
    axl.Feld(),
    axl.Joss(),
    axl.Tullock(),
    axl.UnnamedStrategy(),
    axl.Random()
]

axl_second_players = [
    axl.Black(),
    axl.Borufsen(),
    axl.Cave(),
    axl.Champion(),
    axl.Colbert(),
    axl.Eatherley(),
    axl.Getzler(),
    axl.Gladstein(),
    axl.GoByMajority(),
    axl.GraaskampKatzen(),
    axl.Harrington(),
    axl.Kluepfel(),
    axl.Leyvraz(),
    axl.Mikkelson(),
    axl.MoreGrofman(),
    axl.MoreTidemanAndChieruzzi(),
    axl.RichardHufford(),
    axl.Tester(),
    axl.Tranquilizer(),
    axl.Weiner(),
    axl.White(),
    axl.WmAdams(),
    axl.Yamachi()
]

steward_plotkin_players = [
    axl.ZDExtort2(),
    axl.HardGoByMajority(),
    axl.HardTitForTat(),
    axl.HardTitFor2Tats(),
    axl.GTFT(),
    axl.ZDGTFT2(),
    axl.Calculator(),
    axl.Prober(),
    axl.Prober2(),
    axl.Prober3(),
    axl.HardProber(),
    axl.NaiveProber()
]

case_players = [
    axl.Cooperator(),
    axl.Defector(),
    axl.TitForTat(),
    axl.Grudger(),
    axl.Detective(),
    axl.TitFor2Tats(),
    axl.WinStayLoseShift(),
    axl.Random()
]

best_players = [
    axl.SteinAndRapoport(),
    axl.Grudger(),
    axl.RevisedDowning(),
    axl.TitForTat(),
    axl.Davis(),
    axl.Nydegger(),
    axl.Cave(),
    axl.Tranquilizer(),
    axl.White(),
    axl.Eatherley(),
    axl.Champion(),
    axl.Harrington(),
    axl.Defector(),
    axl.Random(),
    axl.WinStayLoseShift(),
    axl.GTFT(),
    axl.ZDGTFT2(),
    axl.TitFor2Tats(),
    axl.NaiveProber(),
    axl.HardProber()
]

seeds = [1, 771923, 1143728, 291358764, 901236547, 4750670, 511161, 603276, 83281327, 34293471, 918273645, 135792468, 243165978, 9100021, 43238133, 0, 19192831, 5665363, 2231145, 123456]
# seeds = [1, 771923, 1143728, 291358764, 901236547]
# seeds = [4750670, 511161, 603276, 83281327, 34293471]
# seeds = [918273645, 135792468, 243165978, 9100021, 43238133]
# seeds = [0, 19192831, 5665363, 2231145, 123456]
players = []
player_name = ''
for i in range(5):
    if i == 0:
        players = axl_first_players
        player_name = 'axelrod_first'
    elif i == 1:
        players = axl_first_players + axl_second_players
        player_name = 'axelrod_second'
    elif i == 2:
        players = case_players
        player_name = 'case'
    elif i == 3:
        players = steward_plotkin_players + case_players
        player_name = 'steward_plotkin'
    else:
        players = best_players
        player_name = 'best'
    for seed in seeds:
        do_axelrod_tournament(players, 'tournament_axelrod_players_' + player_name + '_param_turns_200_prob_end_0.005_seed_' + str(seed) + '.png', seed=seed, prob_end=0.005)
        do_axelrod_tournament(players, 'tournament_axelrod_players_' + player_name + '_param_turns_200_prob_end_0.005_noise_0.05_seed_' + str(seed) + '.png', seed=seed, prob_end=0.005, noise=0.05)
        do_axelrod_tournament(players, 'tournament_axelrod_players_' + player_name + '_param_turns_200_prob_end_0.005_noise_0.05_biasnoise_seed_' + str(seed) + '.png', seed=seed, prob_end=0.005, noise=0.05, noise_bias=True)
        do_axelrod_tournament(players, 'tournament_axelrod_players_' + player_name + '_param_turns_200_prob_end_0.005_noise_0.2_seed_' + str(seed) + '.png', seed=seed, noise=0.2, prob_end=0.005)
        do_axelrod_tournament(players, 'tournament_axelrod_players_' + player_name + '_param_turns_200_prob_end_0.005_noise_0.2_biasnoise_seed_' + str(seed) + '.png', seed=seed, noise=0.2, prob_end=0.005, noise_bias=True)
        # do_case_tournament(players, 'tournament_case_players_' + player_name + '_param_turns_200_seed_' + str(seed) + '.png', turns=200, maximum_round=50, seed=seed, prob_end=0.005)
        # do_case_tournament(players, 'tournament_case_players_' + player_name + '_param_turns_200_round_50_noise_0.05_seed_'  + str(seed) + '.png', turns=200, maximum_round=50, noise=0.05, seed=seed, prob_end=0.005)
        # do_case_tournament(players, 'tournament_case_players_' + player_name + '_param_turns_200_round_50_noise_0.2_seed_' + str(seed) + '.png', turns=200, maximum_round=50, noise=0.2, seed=seed, prob_end=0.005)
        # do_case_tournament(players, 'tournament_case_players_' + player_name + '_param_turns_200_round_50_noise_0.05_biasnoise_seed_'  + str(seed) + '.png', turns=200, maximum_round=50, noise=0.05, noise_bias=True, seed=seed, prob_end=0.005)
        # do_case_tournament(players, 'tournament_case_players_' + player_name + '_param_turns_200_round_50_noise_0.2_biasnoise_seed_'  + str(seed) + '.png', turns=200, maximum_round=50, noise=0.2, noise_bias=True, seed=seed, prob_end=0.005)

# players = [axl.ZDExtortion(), axl.ZDExtort2(), axl.ZDExtort2v2(), axl.ZDExtort3(), axl.ZDExtort4(), axl.ZDGen2(), axl.ZDGTFT2(), axl.ZDMischief(), axl.ZDSet2(), axl.Cave(), axl.Random()]
# axl.seed(0)
# tournament = axl.Tournament(players)  # Create a tournament
# results = tournament.play()  # Play the tournament
# plot = axl.Plot(results)
# plot.boxplot()
# plt.savefig('boxplot.png', format='png')
# plot.winplot()
# plt.savefig('winplot.png', format='png')
# plot.payoff()
# plt.savefig('payoff.png', format='png')
# plt.close('all')
