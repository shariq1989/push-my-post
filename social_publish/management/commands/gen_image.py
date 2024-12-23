from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont
import os


class Command(BaseCommand):
    help = 'Pin image generation testing'

    def handle(self, *args, **options):
        try:
            command_dir = os.path.dirname(__file__)
            # Define input and output file paths
            input_dir = os.path.join(command_dir, "input")
            output_dir = os.path.join(command_dir, "output")

            # Process all files in the input directory
            if not os.path.exists(input_dir):
                raise FileNotFoundError(f"Input directory '{input_dir}' not found.")

            # Make sure the output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Process each image in the input directory
            for image_filename in os.listdir(input_dir):
                image_file = os.path.join(input_dir, image_filename)
                if os.path.isfile(image_file) and image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    output_file = os.path.join(output_dir, "output_" + image_filename)

                    # Ensure the input image exists
                    if not os.path.exists(image_file):
                        raise FileNotFoundError(f"Input image '{image_file}' not found.")

                    # Define template parameters
                    title = "Decadent Chocolate Cake"
                    highlight = "Perfect for Birthdays!"
                    footer = "www.chocolatelovers.com"

                    # Apply the template
                    self.apply_template(image_file, title, highlight, footer, output_file)

                    # Generate color swatch
                    output_swatch = os.path.join(output_dir, "swatch_" + image_filename)
                    self.get_colors(image_file, output_swatch)

                    self.stdout.write(self.style.SUCCESS(f"Generated image saved as '{output_file}'"))
        except Exception as e:
            raise CommandError(f"Error generating image: {e}")

    def apply_template(self, image_path, title, highlight, footer, output_path):
        try:
            # Load the image
            base_image = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(base_image)

            # Define font path from static/fonts/
            command_dir = os.path.dirname(__file__)
            # Correct the relative path to reach the static/fonts directory
            font_path = os.path.join(command_dir, "fonts/Montserrat-VariableFont_wght.ttf")
            font_path = os.path.abspath(font_path)  # Ensure it's an absolute path
            # Debug font path
            print(f"Using font from: {font_path}")

            # Load the variable font with a specific weight
            title_font = ImageFont.truetype(font_path, 64, encoding="unic")
            highlight_font = ImageFont.truetype(font_path, 32, encoding="unic")
            footer_font = ImageFont.truetype(font_path, 24, encoding="unic")

            # Add text to the image
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
