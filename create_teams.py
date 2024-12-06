"""
Usage: create_teams.py <num_teams>

Arguments:
    num_teams  : Number of teams to create (random pokemon teams to battle with optimized teams in battle_sim.py)
Options:
    -h         : Displays this help file
"""
import docopt
import random
import battle_sim
import pandas as pd
import csv


# Parse command-line arguments
arguments = docopt.docopt(__doc__)
n = int(arguments['<num_teams>'])

# Load data files
pdata = pd.read_csv('data/pokemon_dataset.csv', index_col=0)  # Pokémon base stats and types
mdata = pd.read_csv('data/move_dataset.csv', index_col=0)  # Moves data (power, accuracy, type)
learnset = pd.read_csv('data/learnset_dataset.csv', index_col=0)  # Pokémon move learnset

# Set random seed for reproducibility
random.seed(0)

# Generate `n` random teams
for i in range(n):
    # Create a random team
    team = battle_sim.create_random_team(pdata, mdata, learnset)
    team_indices = [p.i for p in team]  # Pokémon indices in the team
    team_moves = [[m.name for m in p.moves] for p in team]  # Moves assigned to each Pokémon

    # Write the team to a CSV file
    with open(f'teams/random_team_{i}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        for p in range(6):  # Each team has 6 Pokémon
            row = [team_indices[p]] + team_moves[p]  # Pokémon index and its moves
            csvwriter.writerow(row)
