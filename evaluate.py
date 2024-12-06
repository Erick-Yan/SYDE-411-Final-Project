"""
Usage: evaluate.py <filename>

Arguments:
    filename   : The name of the file to evaluate
Options:
    -h         : Displays this help file
"""
import docopt
import pandas as pd
import tqdm
import csv
import random
import battle_sim  # battle_sim functions and classes

# Parse command-line arguments
arguments = docopt.docopt(__doc__)
filename = str(arguments['<filename>'])

# Load Pokémon data, moves, and learnsets
pdata = pd.read_csv('data/pokemon_dataset.csv', index_col=0)  # Pokémon stats and types
mdata = pd.read_csv('data/move_dataset.csv', index_col=0)  # Moves data (type, power, accuracy)
learnset = pd.read_csv('data/learnset_dataset.csv', index_col=0)  # Pokémon learnable moves

# Load the team data from the provided file
team_indices = []  # Stores Pokémon indices in the team
team_moves = []  # Stores moves associated with each Pokémon in the team
with open('teams/' + filename, 'r') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        team_indices.append(int(row[0]))  # Pokémon index
        team_moves.append([int(r) for r in row[1:5]])  # Moves associated with the Pokémon

# Create the optimized team using the battle_similiary Pokémon class
best_team = [battle_sim.Pokemon(i, pdata, mdata, learnset, moves) for i, moves in zip(team_indices, team_moves)]
print([t.name for t in best_team])  # Print the names of the Pokémon in the team

# Initialize results
results = []
random.seed(1)

# Simulate 1000 trials -> should ensure a normal distribution of teams to compare to the optimized teams
for trial in tqdm.tqdm(range(1000)):
    random_team = battle_sim.create_random_team(pdata, mdata, learnset)  # Generate a random team
    for _ in range(10):  # Each trial involves 10 battles
        battle = battle_sim.Battle(best_team, random_team)  # Simulate a battle
        results.append(battle.run())  # Append the result (1 for win, 0 for loss)

# Calculate the win rate
win_rate = sum(results) / len(results)

# Save the win rate to a results file
with open('results/' + filename, 'w') as f:
    f.write(str(win_rate))
