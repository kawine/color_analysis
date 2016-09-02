from tkinter import *
from turtle import *
import turtle

from PIL import Image, ImageDraw

# num_word  : total number of words in the book
# colormap  : [(hex_color, color_term_index), (hex_color, color_term_index), ..]
# width     : Width of the canvas
# height    : Height of the canvas
# line_width: Width of the plotted lines
# filename  : file name of the resulting image
def plot_colors_by_position(num_word, colormap, width, height, line_width, filename):
    # Set up canvas
    img = Image.new('RGB', (width + line_width, height), (255,255,255))
    draw = ImageDraw.Draw(img)

    # Plot lines
    for each in colormap:
        color = "#" + each[0]
        draw.rectangle(((width * (each[1] / num_word), 0),
                        (width * (each[1] / num_word) + line_width, height)),
                        fill=color)

    # Draw outline of the canvas
    draw.rectangle(((0, 0),
                    (width + line_width - 1, height - 1)),
                    outline = "black")

    img.save(filename)


if __name__ == '__main__':

    colormap = [("FF7F50", 10), ("594c26", 15), ("FDD378", 50)]
    plot_colors_by_position(60, colormap, 500, 100, 3, "plot1.png")
