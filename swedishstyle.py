"""
    Swedish style crossword generator

    Copyright © 2022 Martin Ahrnbom
    See the file LICENSE for licensing terms
"""

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


def main():
    c = CrossWord()

if __name__=="__main__":
    main()