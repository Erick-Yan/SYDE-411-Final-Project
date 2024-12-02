"""
Usage:
    pulp_optimizer.py <weight>

Arguments:
    <weight>  The weight to use for optimization (a float between 0 and 1).

Options:
    -h --help  Show this help message.
"""
import pandas as pd
import pulp
import docopt
import csv

arguments = docopt.docopt(__doc__)
stat_weight = float(arguments['<weight>'])


pokemon_df = pd.read_csv('data/pokemon_dataset.csv', index_col=0)
moves_df = pd.read_csv('data/move_dataset.csv', index_col=0) # All Pokemon moves minus banned ones.
learnset_df = pd.read_csv('data/learnset_dataset.csv', index_col=0) # Matrix of whether Pokemon can learn move or not (only Pokemon with >=4 movesets)

# Filter for moves that exist in learnset matrix.
moves_df = moves_df.loc[[int(i) for i in learnset_df.columns]]


roles = ["Physical Sweeper", "Special Sweeper", "Tank", "Mixed Sweeper", "Drainer", "Hybrid"]


# What each type (row) is weak against (column types).
type_effectiveness_matrix = [
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1,],
    [1, 0.5, 2, 1, 0.5, 0.5, 1, 1, 2, 1, 1, 0.5, 2, 1, 1, 1, 0.5, 0.5,],
    [1, 0.5, 0.5, 2, 2, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1,],
    [1, 1, 1, 0.5, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 0.5, 1,],
    [1, 2, 0.5, 0.5, 0.5, 2, 1, 2, 0.5, 2, 1, 2, 1, 1, 1, 1, 1, 1,],
    [1, 2, 1, 1, 1, 0.5, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1,],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 0.5, 1, 1, 0.5, 1, 2,],
    [1, 1, 1, 1, 0.5, 1, 0.5, 0.5, 2, 1, 2, 0.5, 1, 1, 1, 1, 1, 0.5,],
    [1, 1, 2, 0, 2, 2, 1, 0.5, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1,],
    [1, 1, 1, 2, 0.5, 2, 0.5, 1, 0, 1, 1, 0.5, 2, 1, 1, 1, 1, 1,],
    [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 0.5, 2, 1, 2, 1, 2, 1, 1,],
    [1, 2, 1, 1, 0.5, 1, 0.5, 1, 0.5, 2, 1, 1, 2, 1, 1, 1, 1, 1,],
    [0.5, 0.5, 2, 1, 2, 1, 2, 0.5, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 1,],
    [0, 1, 1, 1, 1, 1, 0, 0.5, 1, 1, 1, 0.5, 1, 2, 1, 2, 1, 1,],
    [1, 0.5, 0.5, 0.5, 0.5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2,],
    [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 2, 1, 0.5, 1, 0.5, 1, 2,],
    [0.5, 2, 1, 1, 0.5, 0.5, 2, 0, 2, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 0.5,],
    [1, 1, 1, 1, 1, 1, 0.5, 2, 1, 1, 1, 0.5, 1, 1, 0, 0.5, 2, 1]
]

## 1. Create Role Score Dataset


role_weights = {
    "Physical Sweeper": {
        "HP": 0.3,  # Slight survivability
        "Attack": 1.5,  # Highest priority on raw attack power
        "SpAttack": 0.1,  # Minimal special attack importance
        "Speed": 1.2,  # High importance on speed to strike first
        "Defense": 0.4,  # Some defensive capability
        "SpDefense": 0.3  # Minimal special defense
    },
    "Special Sweeper": {
        "HP": 0.3,  # Slight survivability
        "Attack": 0.1,  # Minimal physical attack importance
        "SpAttack": 1.5,  # Highest priority on special attack power
        "Speed": 1.2,  # High importance on speed to strike first
        "Defense": 0.3,  # Minimal physical defense
        "SpDefense": 0.4  # Some special defensive capability
    },
    "Tank": {
        "HP": 1.5,  # Extreme emphasis on total health
        "Attack": 0.2,  # Minimal offensive capability
        "SpAttack": 0.2,  # Minimal special offensive capability
        "Speed": 0.3,  # Low speed priority
        "Defense": 1.2,  # High physical defense
        "SpDefense": 1.2  # High special defense
    },
    "Mixed Sweeper": {
        "HP": 0.4,  # Balanced survivability
        "Attack": 1,  # Strong physical attack
        "SpAttack": 1,  # Strong special attack
        "Speed": 1,  # Balanced speed
        "Defense": 0.3,  # Minimal physical defense
        "SpDefense": 0.3  # Minimal special defense
    },
    "Drainer": {
        "HP": 1.2,  # High health for sustained combat
        "Attack": 0.3,  # Minimal physical attack
        "SpAttack": 0.3,  # Minimal special attack
        "Speed": 0.4,  # Low speed priority
        "Defense": 1,  # Strong physical defense
        "SpDefense": 1  # Strong special defense
    },
    "Hybrid": {
        "HP": 1,
        "Attack": 1,
        "SpAttack": 1,
        "Speed": 1,
        "Defense": 1,
        "SpDefense": 1
    }
}


def compute_role_score(row, weights):
    return sum(row[stat] * weight for stat, weight in weights.items())


for role, weights in role_weights.items():
    pokemon_df[f"RoleScore_{role}"] = pokemon_df.apply(lambda row: compute_role_score(row, weights), axis=1)

# ## 2. Create Role Move Score Dataset

# **Rationale**:
# - Found common moves for each role here:
#     - http://www.psypokes.com/rsefrlg/roles.php
#     - https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_stat_modification
# - Derived type preferences by analyzing common move types in the second source above.
#     - For Hybrid type preferences, we referenced crowd-sourced data.


role_move_preferences = {
    "Physical Sweeper": ["Earthquake", "Aerial Ace", "Rock Slide", "Brick Break", "Return", "Sludge Bomb", "Shadow Ball", "Belly Drum", "Swords Dance", "Bulk Up", "Dragon Dance"],
    "Special Sweeper": ["Thunderbolt", "Surf", "Ice Beam", "Flamethrower", "Psychic", "Dragon Claw", "Crunch", "Calm Mind", "Rain Dance", "Sunny Day"],
    "Tank": [
        "Acid Armor", "Acupressure", "Ancient Power", "Barrier", "Bulk Up", "Clangorous Soul", 
        "Clangorous Soulblaze", "Coil", "Cosmic Power", "Cotton Guard", "Curse", "Defend Order", 
        "Defense Curl", "Diamond Storm", "Extreme Evoboost", "Flower Shield", "Harden", "Iron Defense", 
        "Max Steelspike", "No Retreat", "Ominous Wind", "Order Up", "Psyshield Bash", "Shelter", 
        "Silver Wind", "Skull Bash", "Steel Wing", "Stockpile", "Stuff Cheeks", "Victory Dance", "Withdraw"
    ],
    "Mixed Sweeper": ["Earthquake", "Thunderbolt", "Surf", "Ice Beam", "Aerial Ace", "Rock Slide", "Brick Break","Swords Dance", "Calm Mind", "Dragon Dance", "Bulk Up"],
    "Drainer": [
        "Absorb", "Bitter Blade", "Bouncy Bubble", "Drain Punch", "Draining Kiss", "Dream Eater", 
        "Giga Drain", "Horn Leech", "Leech Life", "Leech Seed", "Matcha Gotcha", "Mega Drain", 
        "Oblivion Wing", "Parabolic Charge"
    ],
    "Hybrid": []
}
role_type_preferences = {
    "Tank": ["Normal", "Steel", "Fairy", "Fighting", "Ghost"],
    "Hybrid": ["Steel", "Fairy", "Fire", "Water", "Dark"],
    "Drainer": ["Grass", "Fairy", "Fighting", "Flying", "Bug"]
}
role_class_preferences = {
    "Physical Sweeper": ["Physical"],
    "Special Sweeper": ["Special"],
    "Tank": ["Physical", "Special", "Other"],
    "Mixed Sweeper": ["Physical", "Special"],
    "Drainer": ["Physical", "Special", "Other"],
    "Hybrid": ["Physical", "Special", "Other"]
}


def compute_role_move_score(move, role):
    score = 0
    for role_move in role_move_preferences[role]:
        if move["Name"].casefold() in role_move.casefold():
            score += 0.4
            break
    if move["Type"] in role_type_preferences.get(role, []):
        score += 0.3
    if move["Class"] in role_class_preferences[role]:
        score += 0.3
    
    score *= move["Power"] * (move["Accuracy"]/101)
    return score


for role in roles:
    moves_df[f"Effectiveness_{role}"] = moves_df.apply(lambda move: compute_role_move_score(move, role), axis=1)

role_move_scores = moves_df[["Name", "Effectiveness_Physical Sweeper", "Effectiveness_Special Sweeper", "Effectiveness_Tank", "Effectiveness_Mixed Sweeper", "Effectiveness_Drainer", "Effectiveness_Hybrid"]]
for role in roles:
    role_move_scores = role_move_scores.rename(columns={f"Effectiveness_{role}": role})

# ## 3. Prepare Datasets


# Label each role column in mdata as 1 if the move is best representative of a role and 0 otherwise.
effectiveness_columns = [f"Effectiveness_{role}" for role in roles]
max_effectiveness = moves_df[effectiveness_columns].max(axis=1)
for role, col in zip(roles, effectiveness_columns):
    moves_df[role] = (moves_df[col] == max_effectiveness).astype(int)

moves_df = moves_df.drop(columns=effectiveness_columns)


# Get types.
types = list(pokemon_df.columns[-24:-6])


# Get resistances and weaknesses.
type_resistances = {p: {t: int(pokemon_df.loc[p, t] < 1) for t in types} for p in pokemon_df.index}
type_weaknesses = {p: {t: int(pokemon_df.loc[p, t] > 1) for t in types} for p in pokemon_df.index}


# Get which type is effective against other types.
super_effective_types = {a: {t: int(type_effectiveness_matrix[types.index(t)][types.index(moves_df.loc[a]['Type'])] > 1) for t in types} for a in moves_df.index}


# Get STAB.
stab = {p: {a: int(moves_df.loc[a, 'Type'] in [pokemon_df.loc[p, 'Type1'], pokemon_df.loc[p, 'Type2']]) for a in moves_df.index} for p in pokemon_df.index}


indexes = [] # Prepare Y.
pokemon_moves = {} # Prepare hmap for quick reference of moves each Pokemon (index) can learn.
for p in pokemon_df.index:
    pokemon_moves[p] = [int(a) for a in learnset_df.loc[p][learnset_df.loc[p]==1].index]
    indexes += [(p, int(a)) for a in learnset_df.loc[p][learnset_df.loc[p]==1].index]


# Prepare design variable R.
R_list = [(p, s) for p in pokemon_df.index for s in roles]

# ## 4. Setup Optimization Problem


# Setup problem and design variables.
prob = pulp.LpProblem("Strongest Pokemon Team with PuLP", pulp.LpMaximize)
X = pulp.LpVariable.dicts("X", pokemon_df.index, cat=pulp.LpBinary)
Y = pulp.LpVariable.dicts("Y", indexes, cat=pulp.LpBinary)
R = pulp.LpVariable.dicts("R", R_list, cat=pulp.LpBinary)
slack_vars = pulp.LpVariable.dicts("slack", [(p, a, r) for p in pokemon_df.index for a in pokemon_moves[p] for r in roles], 0, 1, cat=pulp.LpContinuous)


# Setup objective functions.
f1 = sum(R[(p, r)] * pokemon_df.loc[p, f"RoleScore_{r}"] for r in roles for p in pokemon_df.index)
f2 = sum((1 + (0.5 * stab[p][a])) * role_move_scores.loc[a, r] * Y[(p, a)] for p in pokemon_df.index for r in roles for a in pokemon_moves[p])
print(stat_weight)
objective_function = (stat_weight * f1) +  ((1-stat_weight) * f2)


prob += objective_function


# Setup constraints.
prob += sum(X[p] for p in pokemon_df.index) == 6 # 6 Pokemon must be selected.
prob += sum(Y[(p, a)] for p in pokemon_df.index for a in pokemon_moves[p]) == 24 # 24 moves allowed total (6 Pokemon, 4 moves each).
prob += sum(R[(p, r)] for p in pokemon_df.index for r in roles) == 6 # 6 roles must be selected (1 role per Pokemon).

for p in pokemon_df.index: # For each Pokemon...
    prob += sum(Y[(p, a)] for a in pokemon_moves[p]) == (4 * X[p]) # Max 4 moves.
    prob += sum(R[(p, r)] for r in roles) == X[p] # Max 1 role.

    # Each Pokemon can only learn moves that are best suited for their role and if they're assigned to that role.
    for r in roles:
        for a in pokemon_moves[p]:
            prob += Y[(p, a)] <= moves_df.loc[a, r] * R[(p, r)] + slack_vars[(p, a, r)]
            prob += slack_vars[(p, a, r)] >= 0

for r in roles: # For each role...
    prob += sum(R[(p, r)] for p in pokemon_df.index) == 1 # There must be at least Pokemon who takes up that role.

for t in types: # For each type...
    # There must be at least 1 move that's super effective against it.
    prob += sum(Y[(p, a)] * super_effective_types[a][t] * (1 - type_weaknesses[p][t]) for p in pokemon_df.index for a in pokemon_moves[p]) >= 1

    # There must be a Pokemon with a type that's resistant to it.
    prob += sum(X[p] * type_resistances[p][t] for p in pokemon_df.index) >= 1

print("Solving...")
prob.solve()
print("Solved!")


print("Selected Pokémon:", [p for p in pokemon_df.index if X[p].varValue == 1])
print("Selected Moves:", [(p, a) for p in pokemon_df.index for a in pokemon_moves[p] if Y[(p, a)].varValue == 1])

# Write results to a CSV file
team = []
team_moves = []

# Gather selected Pokémon and their moves
for p in pokemon_df.index:
    if X[p].varValue == 1:  # If Pokémon is selected
        team.append(p)
        mon_moves = [a for a in pokemon_moves[p] if Y[(p, a)].varValue == 1]  # Selected moves for this Pokémon
        team_moves.append(mon_moves)


filename = f'teams/v2team_={round(stat_weight, 6)}.csv'
selected_pokemon = [p for p in pokemon_df.index if X[p].varValue == 1]
selected_pokemon_roles = {pokemon_df.loc[p, "Name"]: [r for r in roles if R[(p, r)].varValue == 1] for p in selected_pokemon}

# Write to CSV
with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    for i in range(len(team)):  # Loop through the team
        role = selected_pokemon_roles[pokemon_df.loc[selected_pokemon[i], 'Name']]
        row = [team[i]] + team_moves[i] + role  # Pokémon index followed by its moves
        csvwriter.writerow(row)

f1 = 0
print("Calculating f1 (Role Scores):")
for p in pokemon_df.index:
    if X[p].varValue == 1:  # Only consider Pokémon that are part of the team
        for r in roles:
            contribution = R[(p, r)].varValue * pokemon_df.loc[p, f"RoleScore_{r}"]
            print(f"Pokemon: {pokemon_df.loc[p, 'Name']}, Role: {r}, Contribution: {contribution}")
            f1 += contribution

f2 = 0
print("\nCalculating f2 (Move Effectiveness):")
for p in pokemon_df.index:
    for r in roles:
        for a in pokemon_moves[p]:
            stab_bonus = 0.5 * stab[p][a]
            move_contribution = (1 + stab_bonus) * role_move_scores.loc[a, r] * Y[(p, a)].varValue
            print(f"Pokemon: {pokemon_df.loc[p, 'Name']}, Move: {moves_df.loc[a, 'Name']}, "
                  f"Role: {r}, STAB Bonus: {stab_bonus}, "
                  f"Move Score: {role_move_scores.loc[a, r]}, Contribution: {move_contribution}")
            f2 += move_contribution

# Prepare the f_values (rounded)
f_values = [round(f1, 6), round(f2, 6)]
filename = f'results/v2team_f_values={round(stat_weight, 6)}.csv'
with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(f_values)


# selected_pokemon = [p for p in pokemon_df.index if X[p].varValue == 1]
# selected_pokemon_roles = {pokemon_df.loc[p, "Name"]: [r for r in roles if R[(p, r)].varValue == 1] for p in selected_pokemon}
# selected_pokemon_roles_df = pd.DataFrame(list(selected_pokemon_roles.items()), columns=["Pokemon", "Assigned_Roles"])

# selected_moves = [(pokemon_df.loc[p, "Name"], a) for p in pokemon_df.index for a in pokemon_moves[p] if Y[(p, a)].varValue == 1]
# selected_moves_df = pd.DataFrame(selected_moves, columns=["Pokemon", "Move"])
# selected_moves_details_df = moves_df.loc[moves_df.index.isin(selected_moves_df["Move"]), ["Name"]]
# selected_moves_details_df = selected_moves_details_df.rename(columns={"Name": "Move_Name"})
# selected_moves_df = selected_moves_df.merge(selected_moves_details_df, left_on="Move", right_index=True)

# slack_values = []
# for _, row in selected_moves_df.iterrows():
#     pokemon_name = row["Pokemon"]
#     move_name = row["Move"]
#     for role in selected_pokemon_roles[pokemon_name]:
#         slack_value = slack_vars[(pokemon_df[pokemon_df['Name'] == pokemon_name].index[0], move_name, role)].varValue
#         slack_values.append((pokemon_name, move_name, role, slack_value))

# slack_df = pd.DataFrame(slack_values, columns=["Pokemon", "Move", "Role", "Slack_Value"])
# selected_moves_with_slack_df = selected_moves_df.merge(slack_df, on=["Pokemon", "Move"])

# 
# selected_pokemon_roles_df

# 
# selected_moves_with_slack_df





