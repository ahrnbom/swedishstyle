"""
    Swedish style crossword generator

    Copyright © 2022 Martin Ahrnbom
    See the file LICENSE for licensing terms
"""

from dataclasses import dataclass
from pathlib import Path
from random import choice 
from typing import List, Dict 

@dataclass
class Riddle:
    word: str 
    clue: str

class CrossWord:
    def __init__(self, height, width):
        self.height = height
        self.width = width 
        self.letters = dict()
        self.words = list() 

    # No positional checks performed here!
    def add_letter(self, x:int, y:int, letter:str):
        assert len(letter) == 1 
        
        pos = (x, y)
        self.letters[pos] = letter

    # Returns True if successfull. 
    # When False is returned, crossword is not modified
    def try_add_riddle(self, riddle:Riddle, x:int, y:int, horizontal:bool):
        if horizontal:
            dx = 1 
            dy = 0
        else:
            dx = 0
            dy = 1 
        
        to_add = list()

        for letter in riddle.word:
            pos = (x, y)

            if x >= self.width or y >= self.height or x < 0 or y < 0:
                return False 

            if pos in self.letters:
                # Check if another, incompatible, letter is there already
                if self.letters[pos] != letter:
                    return False 

            to_add.append( (pos, letter) )
            x += dx 
            y += dy 

        # Actually add the word
        for pos, letter in to_add:
            self.add_letter(pos[0], pos[1], letter)
        self.words.append( (riddle, pos, horizontal) )

        return True 

    # Loops through all the letters, row first 
    def iterate_letters(self):
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                if pos in self.letters:
                    yield pos, self.letters[pos]
                else:
                    yield pos, None

    def get_density(self):
        n_letters = len(self.letters)
        area = self.width*self.height

        return n_letters/area 


# Data structure to make it easy to find words with letters in certain places
class WordFinder:
    def __init__(self, riddles:List[Riddle]):
        self.by_pos = dict()
        self.by_char = dict()
        self.all = riddles

        for riddle in riddles:
            for i, char in enumerate(riddle.word):
                # By position
                key = (i, char)
                if not key in self.by_pos:
                    self.by_pos[key] = list()
                self.by_pos[key].append(riddle)

                # By letter
                if not char in self.by_char:
                    self.by_char[char] = list()
                
                self.by_char[char].append(riddle)

    def find_by_pos(self, i, char):
        key = (i, char)
        if key in self.by_pos:
            return self.by_pos[key]
        else:
            return list() 

    def find_by_char(self, char):
        if char in self.by_char:
            return self.by_char[char]
        else:
            return list()

def load_riddles(name:str):
    file = Path(f"{name}.words")
    lines = [l for l in file.read_text().split('\n') if l]
    riddles = list()

    for line in lines:
        if ':' in line:
            splot = line.split(':')
            riddle = Riddle(splot[0], splot[1])
        else:
            riddle = Riddle(line, None)
        
        riddles.append(riddle)
    
    return riddles


def brute_force(c:CrossWord, wf:WordFinder):
    # Is the crossword empty? If so, place a random word in top left corner
    if not c.words:
        success = False 
        while not success:
            riddle = choice(wf.all)
            success = c.try_add_riddle(riddle, 1, 0, True)

    


def main():
    c = CrossWord(40,40)

    riddles = load_riddles('disp')
    wf = WordFinder(riddles)


if __name__=="__main__":
    main()