from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont
import os


class Command(BaseCommand):
    help = 'Pin image generation testing'

    def handle(self, *args, **options):
        try:
            command_dir = os.path.dirname(__file__)
            # Define the input and output directories
            input_dir = os.path.join(command_dir, "input")
            output_dir = os.path.join(command_dir, "output")

            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Iterate over all files in the input directory
            for file_name in os.listdir(input_dir):
                # Process only image files (add more extensions if needed)
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    input_image_path = os.path.join(input_dir, file_name)
                    output_image_path = os.path.join(output_dir, f"output_{file_name}")
                    output_swatch_path = os.path.join(output_dir, f"swatch_{file_name}")

                    # Ensure the input image exists
                    if not os.path.exists(input_image_path):
                        raise FileNotFoundError(f"Input image '{input_image_path}' not found.")

                    # Define template parameters
                    title = "Decadent Chocolate Cake"
                    highlight = "Perfect for Birthdays!"
                    footer = "www.chocolatelovers.com"

                    # Apply the template to the image
                    self.apply_template(input_image_path, title, highlight, footer, output_image_path)

                    # Generate the color swatches for the image
                    self.get_colors(input_image_path, output_swatch_path)

                    self.stdout.write(self.style.SUCCESS(f"Generated image and swatch saved as '{output_image_path}' and '{output_swatch_path}'"))

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

            # Add text (title, highlight, footer)
            draw.text((20, 900), title, font=title_font, fill="white")
            draw.text((20, 980), highlight, font=highlight_font, fill="white")
            draw.text((20, 1100), footer, font=footer_font, fill="white")

            # Save the output image
            base_image.save(output_path, "PNG")
        except Exception as e:
            raise CommandError(f"Error applying template: {e}")

    def get_colors(self, image_path, output_file):
        try:
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
        except Exception as e:
            raise CommandError(f"Error generating color swatches: {e}")