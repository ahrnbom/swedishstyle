"""
    Swedish style crossword generator

    Copyright © 2022 Martin Ahrnbom
    See the file LICENSE for licensing terms
"""

from dataclasses import dataclass, is_dataclass, asdict
from pathlib import Path
from random import choice, randint, random 
from typing import List, Dict, Tuple 
import json 

# Allows dataclasses to be JSON encoded
class DCEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

@dataclass
class Riddle:
    word: str 
    clue: str

@dataclass
class PlacedWord:
    riddle: Riddle 
    x: int 
    y: int 
    horizontal: bool

class CrossWord:
    def __init__(self, name, height, width):
        self.name = name 
        self.height = height
        self.width = width 
        self.letters = dict()
        self.placed_words: List[PlacedWord] = list() 

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
        self.placed_words.append(PlacedWord(riddle, pos[0], pos[1], horizontal))

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
    
    def save(self):
        folder = Path(self.name)
        folder.mkdir(exist_ok=True)

        density = self.get_density()
        previous = list(folder.glob('*.crossword'))
        previous.sort()

        if previous:
            best_previous = float(previous[-1].stem)
        else:
            best_previous = 0.0
        
        if density > best_previous:
            path = folder / f"{density:.5f}.crossword"
            obj = dict()
            obj['width'] = self.width
            obj['height'] = self.height
            obj['name'] = self.name 
            obj['words'] = self.placed_words
            with path.open('w', encoding='utf8') as file:
                json.dump(obj, file, cls=DCEncoder, indent=2, ensure_ascii=False)

# Data structure to make it easy to find words with letters in certain places
class WordFinder:
    def __init__(self, riddles:List[Riddle]):
        self.by_pos: Dict[Tuple[int, str], List[Riddle]] = dict()
        self.by_char: Dict[str, List[Riddle]] = dict()
        self.all: List[Riddle] = riddles
        self.used: List[Riddle] = list()

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

    # Returns a deep copy
    def copy(self):
        return WordFinder(self.all)

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
        
    def mark_as_used(self, riddle):
        # Remove from all other data structures
        for i, char in enumerate(riddle.word):
            key = (i, char)
            self.by_pos[key].remove(riddle)

            self.by_char[char].remove(riddle)

        self.used.append(riddle)

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
    if not c.placed_words:
        success = False 
        while not success:
            riddle = choice(wf.all)
            success = c.try_add_riddle(riddle, 1, 0, True)

    c.save()

    # Main algorithm: Find a placed word, select a letter, find another word
    # with that letter, see if it fits. Rinse and repeat
    keep_going = True 
    fail_counter = 0 
    while keep_going:
        placed = choice(c.placed_words)
        letter_pos = randint(0, len(placed.riddle.word)-1)
        letter = placed.riddle.word[letter_pos]

        if letter in wf.by_char and wf.by_char[letter]:
            new_riddle = choice(wf.by_char[letter])
            x = placed.x
            y = placed.y 
            if placed.horizontal:
                x += letter_pos
            else:
                y += letter_pos

            res = c.try_add_riddle(new_riddle, x, y, not placed.horizontal)
            if res: 
                print(f"Added word {new_riddle.word}")
                fail_counter = 0 
                wf.mark_as_used(new_riddle)
                c.save()
            
        fail_counter += 1 
        if fail_counter > len(wf.all)*128:
            keep_going = False 



def main(name):
    c = CrossWord(name, 40,40)

    riddles = load_riddles('test')
    wf = WordFinder(riddles)

    brute_force(c, wf.copy())

if __name__=="__main__":
    main("test")