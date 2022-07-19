"""
    Swedish style crossword generator

    Copyright © 2022 Martin Ahrnbom
    See the file LICENSE for licensing terms
"""

from dataclasses import dataclass
from pathlib import Path 
from typing import List, Dict 

class CrossWord:
    def __init__(self):
        self.height = 0 
        self.width = 0 
        self.letters = dict()

    def add_letter(self, x:int, y:int, letter:str):
        assert len(letter) == 1 
        
        if x > self.width:
            self.width = x

        if y > self.height:
            self.height = y 

        pos = (x, y)
        if pos in self.letters:
            raise ValueError(f"Space {pos} is already occupied")
        
        self.letters[pos] = letter

    # Loops through all the letters, row first 
    def iterate(self):
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                if pos in self.letters:
                    yield pos, self.letters[pos]
                else:
                    yield pos, None

@dataclass
class Riddle:
    word: str 
    clue: str

# Data structure to make it easy to find words with letters in certain places
class WordFinder:
    def __init__(self, riddles:List[Riddle]):
        self.structure = dict()

        for riddle in riddles:
            for i, char in enumerate(riddle.word):
                key = (i, char)
                if not key in self.structure:
                    self.structure[key] = list()
                self.structure[key].append(riddle)

    def find(self, i, char):
        key = (i, char)
        if key in self.structure:
            return self.structure[key]
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

def main():
    c = CrossWord()
    riddles = load_riddles('disp')
    wf = WordFinder(riddles)


if __name__=="__main__":
    main()