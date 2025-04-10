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

    def _text_paint(self, canvas, pin, content):
        canvas.show()
    
    def paint(self, canvas, pin, data_index):
        """
        Adds a single pin to the image of a single row.
        """

        if not isinstance(pin, Pin):
            raise TypeError("Board object tried to paint a non-Pin object")
        
        data_row = self.data.iloc[data_index] # Get the row at index
        content = data_row[pin.col] # Get the data at given column specified in pin

        # Pass the pin, canvas and content to the appropriate paint function
        if isinstance(pin, TextPin):
            self._text_paint(canvas, pin, content)
        elif isinstance(pin, ImagePin):
            print(f"{pin} is an ImagePin")
        else:
            print(f"{pin} is neither a TextPin or ImagePin")
    
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
        """
        Adds a list of pins to the board.
        """

        for arg in args:
            if isinstance(arg, Pin):
                self.pins.append(arg)
            else:
                raise TypeError("Board.pin() method only accepts Pin objects")

class Pin:
    def __init__(self, title, col, pos):
        self.title = title
        self.col = col
        self.pos = pos
    
    def __str__(self):
        return f"Pin: {self.title}, Column: {self.col}, Position: {self.pos}"

class TextPin(Pin):
    def __init__(self, title, col, pos, font, font_size, max_length, fill_mode="shrink"):
        super().__init__(title, col, pos)

        self.font = font
        self.font_size = font_size
        self.max_length = max_length
        self.fill_mode = fill_mode

    def __str__(self):
        return f"TextPin: {self.title}, Column: {self.col}, Position: {self.pos}, Font: {self.font}"

class ImagePin(Pin):
    pass

class PinCondition:
    pass

class Gallery:
    pass