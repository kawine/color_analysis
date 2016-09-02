from PIL import Image, ImageDraw
import colorsys

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
                        fill = color)

    # Draw outline of the canvas
    draw.rectangle(((0, 0),
                    (width + line_width - 1, height - 1)),
                    outline = "black")

    img.save(filename)

# colormap  : {hex_color: frequency, hex_color: frequency, ..}
# width     : Width of the canvas
# height    : Height of the canvas
# filename  : file name of the resulting image
def plot_colors_by_frequency(colormap, width, height, filename):
    # Set up canvas
    img = Image.new('RGB', (width, height), (255,255,255))
    draw = ImageDraw.Draw(img)

    # Sort hex colors
    sorted_colors = list(colormap.keys())
    sorted_colors.sort(key=get_hsv)

    # Count color mentions
    num_distinct_colors = 0
    for key in sorted_colors:
        num_distinct_colors += colormap[key]

    # Plot lines
    cur_x = 0
    for key in sorted_colors:
        color = "#" + key
        draw.rectangle(((cur_x, 0),
                        (cur_x + (width * (colormap[key] / num_distinct_colors)), height)),
                        fill = color)
        cur_x += width * (colormap[key] / num_distinct_colors)

    # Draw outline of the canvas
    draw.rectangle(((0, 0),
                    (width - 1, height - 1)),
                    outline = "black")

    img.save(filename)

# Source: http://stackoverflow.com/questions/8915113/sort-hex-colors-to-match-rainbow
def get_hsv(hexrgb):
    hexrgb = hexrgb.lstrip("#")   # in case you have Web color specs
    r, g, b = (int(hexrgb[i:i+2], 16) / 255.0 for i in range(0,5,2))
    return colorsys.rgb_to_hsv(r, g, b)


if __name__ == '__main__':

    colormap1 = [("FF7F50", 10), ("594c26", 15), ("FDD378", 50)]
    plot_colors_by_position(60, colormap1, 500, 100, 3, "plot_colors_by_position.png")

    colormap2 = {"FF7F50": 10, "594c26": 7, "FDD378": 3}
    plot_colors_by_frequency(colormap2, 500, 100, "plot_colors_by_frequency.png")
