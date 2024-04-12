from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

def insert_spaces(card_number):
    # Insert a space every 4 digits in the card number
    return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

@app.route('/', methods=['GET'])
def generate_credit_card_image():
    # Get parameters from the GET request
    card_number = request.args.get('card_number') or '0000000000000000'
    card_holder = request.args.get('card_holder', 'CARD HOLDER')
    expiration_date = request.args.get('expiration_date', '00/00')
    background_color_param = request.args.get('background_color')  # Optional parameter
    secondary_background_color = request.args.get('background_color_secondary')
    bank_name = request.args.get('bank_name', '')

    # Convert background color parameter to RGB tuple
    if background_color_param:
        try:
            background_color = tuple(map(int, background_color_param.split(',')))
        except ValueError:
            # If provided color is invalid, default to current background color
            background_color = (75, 0, 0)
    else:
        # If background color parameter not provided, default to current background color
        background_color = (75, 0, 0)

    # Convert background color parameter to RGB tuple
    if secondary_background_color:
        try:
            secondary_background_color = tuple(map(int, secondary_background_color.split(',')))
        except ValueError:
            # If provided color is invalid, default to current background color
            secondary_background_color = (255, 150, 150)
    else:
        # If background color parameter not provided, default to current background color
        secondary_background_color = (255, 150, 150)

    # Create a blank image with appropriate dimensions and specified background color
    width, height = 640, 400
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Use default font
    numFont = ImageFont.truetype("VeraMono.ttf", 40)
    expFont = ImageFont.truetype("VeraMono.ttf", 24)
    nameFont = ImageFont.truetype("VeraMono.ttf", 30)
    bankFont = ImageFont.truetype("script.ttf", 50)
    smallFont = ImageFont.truetype("micrenc.ttf", 16)

    # Draw circle in the upper right-hand corner
    circle_color = secondary_background_color  # Choose your desired circle color here
    circle_radius = 400
    circle_x = width
    circle_y = 0
    draw.ellipse([circle_x - circle_radius, circle_y - circle_radius, 
                  circle_x + circle_radius, circle_y + circle_radius], 
                  fill=circle_color)

    # Draw card number with spaces
    card_number_with_spaces = insert_spaces(card_number)
    draw.text((40, 200), f"{card_number_with_spaces}", fill=(200, 200, 200), font=numFont)

    # Draw card holder
    draw.text((40, 340), f"{card_holder.upper()}", fill=(200, 200, 200), font=nameFont)

    # Draw expiration date
    draw.text((40, 260), f"{expiration_date}", fill=(200, 200, 200), font=expFont)

    draw.text((20, 20), f"{bank_name}", fill=(200, 200, 200), font=bankFont)

    draw.text((40, 380), f"{card_number}_{expiration_date.replace('/', '')}", fill=(200, 200, 200), font=smallFont)

    # Draw rectangle in the middle with 6 smaller rectangles inside it
    rectangle_color = (219, 172, 52)  # Choose your desired rectangle color here
    rectangle_width = 100
    rectangle_height = 60
    rectangle_x = (width - rectangle_width) // 5
    rectangle_y = (height - rectangle_height) // 3
    draw.rectangle([rectangle_x, rectangle_y, 
                    rectangle_x + rectangle_width, rectangle_y + rectangle_height], 
                    outline=rectangle_color)
    
    # Draw 6 smaller rectangles inside the middle rectangle in 2 rows
    small_rectangle_color = (219, 172, 52)  # Choose your desired small rectangle color here
    small_rectangle_width = 22
    small_rectangle_height = 20
    small_rectangle_spacing_x = 8
    small_rectangle_spacing_y = 8
    for i in range(2):
        for j in range(3):
            small_rectangle_x = rectangle_x + (rectangle_width - 3 * small_rectangle_width - 2 * small_rectangle_spacing_x) // 2 + j * (small_rectangle_width + small_rectangle_spacing_x)
            small_rectangle_y = rectangle_y + (rectangle_height - 2 * small_rectangle_height - small_rectangle_spacing_y) // 2 + i * (small_rectangle_height + small_rectangle_spacing_y)
            draw.rectangle([small_rectangle_x, small_rectangle_y,
                            small_rectangle_x + small_rectangle_width, small_rectangle_y + small_rectangle_height],
                           fill=small_rectangle_color)

    # Open the "visa.png" image
    visa_image = Image.open("visa.png")
    if visa_image.mode != "RGBA":
        visa_image = visa_image.convert("RGBA")
    # Resize the visa image to approximately 50 pixels wide while maintaining aspect ratio
    visa_image.thumbnail((150, 150))
    # Calculate the position to paste the visa image (bottom right corner)
    visa_width, visa_height = visa_image.size
    paste_x = width - visa_width - 10  # 10 is a padding value
    paste_y = height - visa_height  # 10 is a padding value
    # Paste the visa image onto the generated image
    image.paste(visa_image, (paste_x, paste_y), mask=visa_image)

    # Save image to byte stream
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)

    return img_byte_array.getvalue(), 200, {'Content-Type': 'image/png'}

if __name__ == '__main__':
    app.run(debug=True, port=10000, host="0.0.0.0")
