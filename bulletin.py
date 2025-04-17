from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os

class Board:
    def __init__(self, data, dimensions=(500,500), output_format="png", mode="RGBA", background_color=None):
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
    
    def new_canvas(self):
        """
        Returns a blank image with the board's specified mode and background color
        """

        return Image.new(self.mode, self.dimensions, self.background_color)

    def _text_paint(self, draw: ImageDraw.ImageDraw, pin: "TextPin", content):
        def _fit_font_size(content, initial_font_size, font_face, init_text_width, max_width):
            """
            Given a font, some text and a maximum width, calculate the optimal font size.
            """
            current_font_size = initial_font_size
            text_width = init_text_width

            ## FIXME: Sometimes the current_font_size oscillates between two values,
            ## never meeting the loop condition, creating an infinite loop.
            ## Temporarily fixed by changing the condition to be more forgiving

            while not max_width-(0.05*max_width) <= text_width <= max_width:
                # Calculate the length of the text with the current font size
                font = ImageFont.truetype(font_face, int(current_font_size))
                bbox = font.getbbox(content)
                text_width = bbox[2] - bbox[0]

                # Calculate the proportion between the difference and the max width
                diff = max_width - text_width
                proportion = diff / text_width

                # Update current font size according to the proportion
                current_font_size *= (1+proportion)

            return current_font_size
        def _wrap_text(content, font_size, font_face, max_width, wrap_mode):
            """
            Given a font and some text, wrap the text either by character or by word.
            """

            result = []

            for original_line in content.split("\n"):
                if not original_line:
                    # Keep empty lines
                    result.append("")
                    continue
                
                current_line = ""

                # Split line into tokens, depending on wrap mode
                # For 'wrap', split into characters. For 'wordwrap', split into words.
                if wrap_mode == "wrap":
                    tokens = tuple(original_line)
                elif wrap_mode == "wordwrap":
                    tokens = original_line.split(" ")
                
                # Process each token
                for token in tokens:
                    # Test if adding this token would exceed the max width
                    test_line = current_line + token
                    init_font = ImageFont.truetype(font_face, font_size)
                    bbox = init_font.getbbox(test_line)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= max_width:
                        # Token fits, add it to the current line
                        current_line += token
                        if wrap_mode == "wordwrap":
                            current_line += " "
                    else:
                        # Token doesn't fit, start a new line
                        result.append(current_line)
                        current_line = token
                        if wrap_mode == "wordwrap":
                            current_line += " "
                
                # Add the last line segment
                if current_line:
                    result.append(current_line)

            # Join all lines with newlines
            return ('\n'.join(result)).lstrip()

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
            font_size = _fit_font_size(content, pin.font_size, pin.font_face, text_width, pin.max_width)
            font = ImageFont.truetype(pin.font_face, font_size)
        else:
            font = init_font

            if pin.fill_mode == "wrap" or pin.fill_mode == "wordwrap":
                content = _wrap_text(content, pin.font_size, pin.font_face, pin.max_width, pin.fill_mode)

        draw.text(pin.pos, content, font=font, fill=pin.color, align=pin.align)
    
    def _image_paint(self, canvas: Image.Image, pin: "ImagePin" , content):
        """
        Adds an image pin to the current canvas.
        """

        # Load corresponding image from gallery.
        image = None

        for img_format in ("png", "jpg", "bmp", "svg", "heic"):
            try:
                image = Image.open(f'{pin.gallery}/{content}.{img_format}')
            except:
                pass
            else:
                break
        
        # Check if image exists
        if not image:
            raise FileNotFoundError(f"Image {pin.gallery}/{content} does not exist or is not in acceptable format.")
        else:
            # Adjust image size to dimensions according to fill mode
            if pin.fill_mode == "stretch":
                image = image.resize(pin.dimensions)
            elif pin.fill_mode == "fit":
                # Calculate the optimal dimensions
                img_width, img_height = image.size
                max_width, max_height = pin.dimensions
                optimal_width, optimal_height = 0, 0
                
                # If width is larger than height
                if img_width / img_height > 1:
                    # Width is the limiting factor
                    proportion = max_width / img_width
                    optimal_width = int(proportion * img_width)
                    optimal_height = int(proportion * img_height)
                else:
                    # Height is the limiting factor
                    proportion = max_height / img_height
                    optimal_width = int(proportion * img_width)
                    optimal_height = int(proportion * img_height)
                
                image = image.resize((optimal_width, optimal_height))

            # Add image to canvas
            canvas.paste(image, pin.pos, image)
    
    def paint(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, pin: "Pin", data_index):
        """
        Adds a single pin to the current canvas.
        """

        # Validate argument types
        if not isinstance(pin, Pin):
            raise TypeError("Board tried to paint a non-Pin object.")
        if not isinstance(draw, ImageDraw.ImageDraw):
            raise TypeError("Board.paint() draw argument is not ImageDraw object.")
        
        data_row = self.data.iloc[data_index] # Get the row at index
        content = data_row[pin.col] # Get the data at given column specified in pin
 
        # Pass the pin, canvas and content to the appropriate paint function
        if isinstance(pin, TextPin):
            self._text_paint(draw, pin, content)
        elif isinstance(pin, ImagePin):
            self._image_paint(canvas, pin, content)
        else:
            print(f"{pin} is neither a TextPin or ImagePin")
    
    def post(self, data_index, save=True, display=False, filepath=None):
        """
        Creates the appropriate image for a single row of the data.
        """
        
        # Create canvas and draw object
        canvas = self.new_canvas()
        draw = ImageDraw.Draw(canvas)

        # Add the pins to the canvas
        for pin in self.pins:
            self.paint(canvas, draw, pin, data_index)
        
        # Display and/or save image
        if display:
            canvas.show()
        
        if save:
            if filepath is None:
                filepath = f"board-post{data_index}.{self.output_format}"
            else:
                filepath += f'.{self.output_format}'
            
            canvas.save(filepath)
        
    def blueprint(self):
        """
        Creates a post, but with all pins displaying their titles.
        """
        pass

    def publish(self, folder="posts", truncate_old_posts=True):
        """
        Creates all the images for the data, and stores them in specified folder.
        """

        try:
            # Make folder
            os.makedirs(folder)
        except FileExistsError:
            # If the foler already exists and the user wishes to truncate old posts, delete all files in folder.
            if truncate_old_posts:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename) 
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)  
                        elif os.path.isdir(file_path):  
                            os.rmdir(file_path)  
                    except Exception as e:  
                        print(f"Error deleting {file_path}: {e}")
                
                print(f'Folder "{folder}" has been truncated.')
        finally:
            # Make posts
            for i in range(len(self.data)):
                self.post(i, filepath=f"{folder}/board-post{i}")
        
        print(f'Posts successfully published in folder "{folder}".')

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
    def __init__(self, title, col, pos, font, font_size=32, color=(0,0,0), max_width=1000, fill_mode="shrink", default_text=None, align="left", anchor="topright"):
        super().__init__(title, col, pos)

        if not col and not default_text:
            raise ValueError(f"TextPin must have column or default text or both.")
        if default_text is None:
            self.default_text = self.title

        self.default_text = default_text

        self.font_face = font
        self.font_size = font_size
        self.color = color

        self.max_width = max_width
        if fill_mode in ("fill", "shrink", "cut", "wrap", "wordwrap", "fixed"):
            self.fill_mode = fill_mode
        else:
            raise ValueError(f"Invalid fill mode for TextPin: {fill_mode}, must be fill, shrink, cut, wrap, wordwrap or fixed")
        
        self.align = align
        self.anchor = anchor

    def __str__(self):
        return f"TextPin: {self.title}, Column: {self.col}, Position: {self.pos}, Font Face: {self.font_face}, Font Size: {self.font_size}"

class ImagePin(Pin):
    def __init__(self, title, col, pos, gallery, default_image=None, dimensions=None, fill_mode="fit", anchor="topright"):
        super().__init__(title, col, pos)

        if not col and not default_image:
            raise ValueError("ImagePin must have column or default image or both.")

        self.gallery = gallery
        self.default_image = default_image

        self.dimensions = dimensions
        if fill_mode in ("fit", "stretch", "fixed"):
            self.fill_mode = fill_mode
        else:
            raise ValueError(f"Invalid fill mode for ImagePin: {fill_mode}, must be fit, stretch or fixed")

        self.anchor = anchor
    
    def __str__(self):
        return f"ImagePin: {self.title}, Column: {self.col}, Position: {self.pos}, Gallery: {self.gallery}"

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