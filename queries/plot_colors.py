from tkinter import *
from turtle import *
import turtle

# Creates eps file
def plot_colors_by_position(num_word, colormap, filename):

    # Set up canvas
    width, height, line_width = 500, 100, 2
    turtle.setup(width + line_width, height)
    turtle.hideturtle()
    orig = ((width + line_width)/2, height/2)
    t = turtle.Turtle()
    #t.speed(0)

    # Plot lines
    t.pensize(line_width)
    for each in colormap:
        t.color("#" + each[0])
        t.up()
        t.sety(-orig[1])
        t.setx(width * (each[1] / num_word) - orig[0])
        t.down()
        t.sety(height)

    # Draw border
    t.pensize(1)
    t.color("#000000")
    t.up()
    t.setx(-orig[0] + 5)
    t.sety(orig[1] - 5)
    t.down()
    t.setx(orig[0] - 14)
    t.sety(-orig[1] + 14)
    t.setx(-orig[0] + 5)
    t.sety(orig[1] - 5)

    # Save the image
    ts = turtle.getscreen()
    ts.getcanvas().postscript(file=filename)


if __name__ == '__main__':

    # colormap should look like
    # [(hex_color, index), (hex_color, index), ..]
    colormap = [("FF7F50", 10), ("594c26", 15), ("FDD378", 50)]
    plot_colors_by_position(60, colormap, "plot1.eps")
