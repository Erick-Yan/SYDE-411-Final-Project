import random

types = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

# Class to represent a Pokémon
class Pokemon:
    def __init__(self, i, pdata, mdata, learnset, moves=None):
        self.i = i
        row = pdata.loc[i]
        possible_moves = list(learnset.loc[i][learnset.loc[i] == 1].index)
        self.name = row['Name']
        self.types = [row['Type1'], row['Type2']]
        self.hp = int((2 * row['HP'] * 50) / 100) + row['HP'] + 50
        self.attack = int((2 * row['Attack'] * 50) / 100 + 5)
        self.spattack = int((2 * row['SpAttack'] * 50) / 100 + 5)
        self.defense = int((2 * row['Defense'] * 50) / 100 + 5)
        self.spdefense = int((2 * row['SpDefense'] * 50) / 100 + 5)
        self.speed = int((2 * row['Speed'] * 50) / 100 + 5)
        self.effectiveness = {t: row[t] for t in types}
        if moves:
            self.moves = [mdata.loc[int(a)] for a in moves]
        else:
            self.moves = [mdata.loc[int(a)] for a in random.sample(possible_moves, 4)]
        self.current_hp = self.hp
    
    def reset(self):
        self.current_hp = self.hp
    
    def __repr__(self):
        return self.name
    
    def calculate_damage(self, move, enemy):
        stab = 1 + (int(move['Type'] in self.types) / 2)
        if move['Class'] == 'Physical':
            multiplier = self.attack / enemy.defense
        elif move['Class'] == 'Special':
            multiplier = self.spattack / enemy.spdefense
        damage = int((((22 * move['Power'] * multiplier) / 50) + 2) * stab * enemy.effectiveness[move['Type']])
        return damage

    def choose_move(self, enemy):
        possible_damages = [self.calculate_damage(m, enemy) for m in self.moves]
        best_move_index = max((x, i) for i, x in enumerate(possible_damages))[1]
        return self.moves[best_move_index]
    
    def attack_action(self, enemy, move):
        chance = random.random() * 100
        if chance < move['Accuracy']:
            rand_modifier = random.randint(85, 100)
            damage = int(self.calculate_damage(move, enemy) * (rand_modifier / 100))
        else:
            damage = 0
        enemy.current_hp = max(enemy.current_hp - damage, 0)


# Class to simulate a battle between two teams
class Battle:
    def __init__(self, team1, team2):
        self.team = team1
        self.enemy_team = team2
        for pokemon1, pokemon2 in zip(self.team, self.enemy_team):
            pokemon1.reset()
            pokemon2.reset()
        self.current_pokemon = random.choice(range(6))
        self.current_enemy_pokemon = random.choice(range(6))
        self.wins = 0
        self.enemy_wins = 0
    
    def run(self):
        turn = 0
        while self.wins != 6 and self.enemy_wins != 6 and turn < 3000:
            my_pokemon = self.team[self.current_pokemon]
            enemy_pokemon = self.enemy_team[self.current_enemy_pokemon]
            if my_pokemon.speed < enemy_pokemon.speed:
                first = enemy_pokemon
                second = my_pokemon
            elif enemy_pokemon.speed < my_pokemon.speed:
                first = my_pokemon
                second = enemy_pokemon
            else:
                first, second = random.sample([my_pokemon, enemy_pokemon], 2)
            first_move = first.choose_move(second)
            second_move = second.choose_move(first)
            first.attack_action(second, first_move)
            if second.current_hp > 0:
                second.attack_action(first, second_move)
            
            if my_pokemon.current_hp == 0:
                self.enemy_wins += 1
                if self.enemy_wins != 6:
                    self.current_pokemon = random.choice([i for i, p in enumerate(self.team) if p.current_hp > 0])
            if enemy_pokemon.current_hp == 0:
                self.wins += 1
                if self.wins != 6:
                    self.current_enemy_pokemon = random.choice([i for i, p in enumerate(self.enemy_team) if p.current_hp > 0])
            turn += 1
        return self.wins == 6
    
# Function to create a random team
def create_random_team(pdata, mdata, learnset):
    return [Pokemon(i, pdata, mdata, learnset) for i in random.sample(list(pdata.index), 6)]
