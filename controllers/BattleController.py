import time

import pygame

from fixtures.constants import *
from graphics.Screen import Screen
from graphics.views.BattleView import BattleView
from graphics.views.QuestionView import QuestionView
from graphics.TextUtil import TextUtil
from utils import load_random_question, keyboard_control


class BattleController:
    def __init__(self, character, monster, has_question=False):
        self.character = character
        self.monster = monster
        self.won = False
        self.hp_lost = 0
        self.boost = 0
        if has_question:
            self.question_view = QuestionView(load_random_question(), self)
            self.battle_view = BattleView(self, self.question_view)
        else:
            self.battle_view = BattleView(self)
        self.bring_character_back_to_life_action = {
            pygame.K_y: self.bring_character_back_to_life,
            pygame.K_n: self.end_game
        }

    def start_battle_view(self):
        self.battle_view.display()
        return self.won

    def start_battle(self):
        while self.character.hp > 0 and self.monster.hp > 0:
            self.battle_player_strike()
            if self.monster.hp > 0:
                self.battle_monster_strike()

        if self.character.hp <= 0:
            for item in self.character.items:
                if item.name == life_renewal_potion_item_name:
                    self.display_cure_character_text()
                    break
            else:
                self.end_game()

    def battle_won_result(self):
        self.won = True
        self.character.exp += self.monster.xp
        return ['You win!', f'You lost {self.hp_lost} hp and gained {self.monster.xp} xp.']

    def battle_lost_result(self):
        self.won = False
        return ['You lost!']

    def battle_player_strike(self):
        strike_amount = self.character.strength + self.boost + self.character.exp // 10
        self.monster.hp -= strike_amount
        self.battle_view.display_round(f'You hit monster with {strike_amount} damage.')
        if self.monster.hp <= 0:
            self.battle_view.invoke_battle_won()

    def battle_monster_strike(self):
        strike_amount = self.monster.strength
        self.character.hp -= strike_amount
        self.hp_lost += strike_amount
        self.battle_view.display_round(f'Monster hit you with {strike_amount} damage.')
        if self.character.hp <= 0:
            self.battle_view.invoke_battle_lost()

    def accept_answer(self):
        self.boost = 3
        Screen.display_surface.fill(black)
        self.battle_view.render_line_center('You got bonus damage of ' + str(self.boost), 1)
        time.sleep(1)

    def reject_answer(self):
        self.boost = 0

    def display_cure_character_text(self):
        Screen.display_surface.fill(black)
        text_util = TextUtil((0, 0), (0, 0))
        text_util.print_multiline('You lost the battle, but you can save yourself because you have a magic HP Potion.'
                                  'Do you want to use it? (Y - yes, N - no)')
        keyboard_control(self.bring_character_back_to_life_action)
        time.sleep(1)

    def bring_character_back_to_life(self):
        for item in self.character.items:
            if item.name == life_renewal_potion_item_name:
                self.character.hp = item.healing
                self.character.remove_item(item)
                pygame.display.update()
                break

    def end_game(self):
        self.battle_view.display_game_ending(self.character.exp, False)
