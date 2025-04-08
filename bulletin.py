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
    
    def paint(self, pin, data_index):
        """
        Adds a single pin to the image of a single row.
        """

        if type(pin) is not Pin:
            raise TypeError("Board object tried to paint a non-Pin object")
        
        data_row = self.data.iloc[data_index] # Get the row at index
        content = data_row[pin.col] # Get the data at given column specified in pin

        print(content)
    
    def post(self, data_index):
        """
        Creates the appropriate image for a single row of the data.
        """
        pass

    def publish(self):
        """
        Creates all the images for the data.
        """
        pass

    def pin(self, *args):
        for arg in args:
            if type(arg) is Pin:
                self.pins.append(arg)
            else:
                raise TypeError("Board.pin() method only accepts Pin objects")

class Pin:
    def __init__(self, title, col):
        self.title = title
        self.col = col
    
    def __str__(self):
        return f"Pin: {self.title}, Column: {self.col}"

class TextPin(Pin):
    pass

class ImagePin(Pin):
    pass

class PinCondition:
    pass

class Gallery:
    pass