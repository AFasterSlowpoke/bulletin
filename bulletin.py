from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class Board:
    def __init__(self, data, dimensions=(500,500), output_format="jpg", mode="RGBA", background_color=None):
        self.data = data

        self.dimensions = dimensions
        self.output_format = output_format
        self.mode = mode
        if background_color is None:
            # Default background_color changes depending on image mode
            if mode == "RGBA":
                self.background_color = (255,255,255,255)
            else:
                self.background_color = (255,255,255)
        else:
            self.background_color = background_color

        self.pins = []
    
    def __str__(self):
        pins_string = ""
        for pin in self.pins:
            pins_string += f"{str(pin)}\n"
        
        return f"Board\n{len(self.pins)} Pins\n__________\n{pins_string}"
    
    def canvas(self):
        """
        Returns a blank image with the board's specified mode and background color
        """

        return Image.new(self.mode, self.dimensions, self.background_color)

    def _text_paint(self, draw: ImageDraw.ImageDraw, pin: "TextPin", content):
        def _fit_font_size(content, initial_font_size, font_face, init_text_width):
            current_font_size = initial_font_size
            text_width = init_text_width

            ## FIXME: Sometimes the current_font_size oscillates between two values,
            ## never meeting the loop condition, creating an infinite loop.
            ## Temporarily fixed by changing the condition to be more forgiving

            while not pin.max_width-(0.05*pin.max_width) <= text_width <= pin.max_width:
                # Calculate the length of the text with the current font size
                font = ImageFont.truetype(font_face, int(current_font_size))
                bbox = font.getbbox(content)
                text_width = bbox[2] - bbox[0]

                # Calculate the proportion between the difference and the max width
                diff = pin.max_width - text_width
                proportion = diff / text_width

                # Update current font size according to the proportion
                current_font_size *= (1+proportion)

            return current_font_size
        def _wrap_text(content, font_size, font_face, max_width):
            result = []

            for original_line in content.split('\n'):
                if not original_line:
                    # Keep empty lines
                    result.append("")
                    continue
                
                current_line = ""
                
                # Process each character in the line
                for char in original_line:
                    # Test if adding this character would exceed the max width
                    test_line = current_line + char
                    init_font = ImageFont.truetype(font_face, font_size)
                    bbox = init_font.getbbox(test_line)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= max_width:
                        # Character fits, add it to the current line
                        current_line += char
                    else:
                        # Character doesn't fit, start a new line
                        result.append(current_line)
                        current_line = char
                
                # Add the last line segment
                if current_line:
                    result.append(current_line)

            # Join all lines with newlines
            return '\n'.join(result)

        """
        Adds a text pin to the current canvas.
        """

        # Create inital font and get initial text width
        init_font = ImageFont.truetype(pin.font_face, pin.font_size)
        bbox = init_font.getbbox(content)
        text_width = bbox[2] - bbox[0]

        # If the fill mode is "fill" or the fill mode is "shrink" and the text doesn't fit within the max length,
        # fit the font size to the maximum length. Otherwise, use the initial font.
        if pin.fill_mode == "fill" or (text_width > pin.max_width and pin.fill_mode == "shrink"):
            font_size = _fit_font_size(content, pin.font_size, pin.font_face, text_width)
            font = ImageFont.truetype(pin.font_face, font_size)
        else:
            font = init_font

            if pin.fill_mode == "wrap":
                content = _wrap_text(content, pin.font_size, pin.font_face, pin.max_width)

        draw.text(pin.pos, content, font=font, fill=pin.color, align=pin.align)
    
    def paint(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, pin: "Pin", data_index):
        """
        Adds a single pin to the current canvas.
        """

        # Validate argument types
        if not isinstance(pin, Pin):
            raise TypeError("Board tried to paint a non-Pin object.")
        if not isinstance(canvas, Image.Image):
            raise TypeError("Board.paint() canvas argument is not Image object.")
        if not isinstance(draw, ImageDraw.ImageDraw):
            raise TypeError("Board.paint() draw argument is not ImageDraw object.")
        
        data_row = self.data.iloc[data_index] # Get the row at index
        content = data_row[pin.col] # Get the data at given column specified in pin
 
        # Pass the pin, canvas and content to the appropriate paint function
        if isinstance(pin, TextPin):
            self._text_paint(draw, pin, content)
        elif isinstance(pin, ImagePin):
            print(f"{pin} is an ImagePin")
        else:
            print(f"{pin} is neither a TextPin or ImagePin")

        canvas.show()
    
    def post(self, data_index):
        """
        Creates the appropriate image for a single row of the data.
        """
        pass

    def blueprint(self):
        """
        Creates a post, but with all pins displaying their titles.
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
    def __init__(self, title, col, pos, font, font_size=32, color=(0,0,0), max_width=1000, fill_mode="shrink", align="left"):
        super().__init__(title, col, pos)

        self.font_face = font
        self.font_size = font_size
        self.color = color

        self.max_width = max_width
        if fill_mode in ("fill", "shrink", "cut", "wrap", "wordwrap", "fixed"):
            self.fill_mode = fill_mode
        else:
            raise ValueError(f"Invalid fill mode for TextPin: {fill_mode}, must be fill, shrink, cut, wrap, wordwrap or fixed")
        self.align = align

    def __str__(self):
        return f"TextPin: {self.title}, Column: {self.col}, Position: {self.pos}, Font Face: {self.font_face}, Font Size: {self.font_size}"

class ImagePin(Pin):
    pass

class PinCondition:
    pass

class Gallery:
    pass

def read_from_gsheet(sheet_name, sheet_id, table_id='0'):
    """
    Returns pandas dataframe of table of Google sheet with specified sheet name, sheet ID and table ID.
    Your Google sheet must not be restricted for this function to work.
    """

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}&gid={table_id}"

    return pd.read_csv(url)