from bulletin import Board, TextPin, ImagePin, read_from_gsheet, read_from_excel

#response_data = read_from_gsheet("BulletinTestData", "1br5l-96rxedgr00yXyZZAoV2A8Fn_YpfHtM3r8mKqug")
response_data = read_from_excel("BulletinTestData.xlsx", "Sheet1")

 
board = Board(response_data, background="background.jpg")


author = TextPin(
    title="Response Author",
    col="Author",
    pos=(675, 300),
    default="Sausiiie",
    font="hanken-grotesk-bold.ttf",
    font_size=64,
    max_width=450,
    color=(255,255,255,255),
    fill_mode="shrink",
    anchor="bottomleft"
)

response = TextPin(
    title="Response",
    col="Response",
    pos=(650, 400),
    font="HankenGrotesk.ttf",
    font_size=32,
    max_width=600,
    color=(255,255,255,255),
    fill_mode="wordwrap"
)

booksona = ImagePin(
    title="Booksona",
    col="Author",
    pos=(150, 250),
    default="Sausiiie",
    gallery="booksonas",
    dimensions=(500,500),
    fill_mode="stretch"
)


board.pin(author, response, booksona)


board.publish(folder="responses")
