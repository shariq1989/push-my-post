from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont
import os


class Command(BaseCommand):
    help = 'Pin image generation testing'

    # Get the directory of the current command file

    def handle(self, *args, **options):
        try:
            command_dir = os.path.dirname(__file__)
            # Define input and output file paths
            image_file = os.path.join(command_dir, "img2.jpg")  # Ensure the file name matches
            output_file = os.path.join(command_dir, "output_" + "img2.jpg")

            # Ensure the input image exists
            if not os.path.exists(image_file):
                raise FileNotFoundError(f"Input image '{image_file}' not found.")

            # Define template parameters
            title = "Decadent Chocolate Cake"
            highlight = "Perfect for Birthdays!"
            footer = "www.chocolatelovers.com"

            # Apply the template
            self.apply_template(image_file, title, highlight, footer, output_file)
            output_swatch = os.path.join(command_dir, "swatch_" + "img2.jpg")
            self.get_colors(image_file, output_swatch)
            self.stdout.write(self.style.SUCCESS(f"Generated image saved as '{output_file}'"))
        except Exception as e:
            raise CommandError(f"Error generating image: {e}")

    def apply_template(self, image_path, title, highlight, footer, output_path):
        try:
            # Load the image
            base_image = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(base_image)

            # Define fonts (ensure the font files exist on your system)
            command_dir = os.path.dirname(__file__)
            font_path = os.path.join(command_dir, "Roboto-Black.ttf")
            title_font = ImageFont.truetype(font_path, 64)
            highlight_font = ImageFont.truetype(font_path, 32)
            footer_font = ImageFont.truetype(font_path, 24)

            # Add text
            draw.text((20, 900), title, font=title_font, fill="white")
            draw.text((20, 980), highlight, font=highlight_font, fill="white")
            draw.text((20, 1100), footer, font=footer_font, fill="white")

            # Save the output image
            base_image.save(output_path, "PNG")
        except Exception as e:
            raise CommandError(f"Error applying template: {e}")

    def get_colors(self, image_path, output_file):
        # Open the image
        image = Image.open(image_path)

        # Quantize to reduce the image to 10 colors
        quantized = image.quantize(colors=10)

        # Extract the palette
        palette = quantized.getpalette()
        dominant_colors = [tuple(palette[i:i + 3]) for i in range(0, len(palette), 3)]

        # Print the dominant colors
        print("Dominant colors:", dominant_colors[:10])

        # Create a new image for color swatches
        swatch_width = 100
        swatch_height = 100
        swatch_image = Image.new("RGB", (swatch_width * len(dominant_colors), swatch_height))

        # Create drawing object
        draw = ImageDraw.Draw(swatch_image)

        # Draw color swatches
        for i, color in enumerate(dominant_colors):
            # Draw a rectangle for each color
            draw.rectangle([i * swatch_width, 0, (i + 1) * swatch_width, swatch_height], fill=color)

        # Save the swatch image
        swatch_image.save(output_file)
        print(f"Color swatches saved to {output_file}.")

def create_bold_centered_text_template(image_path, output_path, text):
    """
    Creates a Pinterest template with a bold, centered text on top of a black overlay in the middle of the image.
    """
    # Open the image
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    # Create an overlay with black color in the center
    overlay_height = int(height * 0.25)  # 25% of the image height
    overlay_width = int(width * 0.8)  # 80% of the image width

    overlay = Image.new("RGBA", (overlay_width, overlay_height), (0, 0, 0, 128))  # semi-transparent black
    overlay_x = (width - overlay_width) // 2  # Center the overlay horizontally
    overlay_y = (height - overlay_height) // 2  # Center the overlay vertically

    # Paste the overlay onto the image
    image.paste(overlay, (overlay_x, overlay_y), overlay)

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Define the font (bold white text)
    try:
        font = ImageFont.truetype("arial.ttf", 64, encoding="unic")
    except IOError:
        font = ImageFont.load_default()  # Fallback if the font is not found

    # Calculate text size and position
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (width - text_width) // 2  # Center the text horizontally
    text_y = (height - text_height) // 2  # Center the text vertically

    # Add the text to the image
    draw.text((text_x, text_y), text, font=font, fill="white")

    # Save the output image
    image.save(output_path, "PNG")
    print(f"Bold Centered Text template created and saved as {output_path}.")