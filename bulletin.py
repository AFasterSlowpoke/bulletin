from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class Board:
    def __init__(self, data, dimensions=(500,500), output_format="jpg", background=None):
        self.data = data

        self.dimensions = dimensions
        self.output_format = output_format

        self.pins = []
    
    def __str__(self):
        pins_string = ""
        for pin in self.pins:
            pins_string += f"{str(pin)}\n"
        
        return f"Board\n{len(self.pins)} Pins\n__________\n{pins_string}"
    
    def post(self, index):
        pass

    def publish(self):
        pass

    def pin(self, *args):
        for arg in args:
            if type(arg) is Pin:
                self.pins.append(arg)
            else:
                raise TypeError("Board.pin() method only accepts Pin objects")

class Pin:
    def __init__(self, title):
        self.title = title
    
    def __str__(self):
        return f"Pin: {self.title}"

class TextPin(Pin):
    pass

class ImagePin(Pin):
    pass

class PinCondition:
    pass

class Gallery:
    pass