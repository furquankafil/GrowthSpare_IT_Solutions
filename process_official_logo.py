"""
Corporate Logo Crop & Favicon Processing Engine for GrowthSpare IT Solutions.
Loads your official uploaded logo ('static/images/logo.png'), programmatically
extracts the 'GS' monogram symbol from the left portion, and compiles it
into a multi-size web standard 'favicon.ico' browser tab icon.

Prerequisites:
- Requires 'Pillow' (already installed via requirements.txt).
- Make sure you save your official logo as 'static/images/logo.png' first.

Usage:
- Run 'python process_official_logo.py' in your PowerShell terminal.
"""

import os
from PIL import Image


def process_logo_to_favicon():
    logo_path = os.path.join("static", "images", "logo.png")
    favicon_path = os.path.join("static", "images", "favicon.ico")

    # Guard check to ensure the logo has been saved by the user first [1]
    if not os.path.exists(logo_path):
        print("==============================================================================")
        print("CRITICAL ERROR: Official logo not found on disk!")
        print("Please save your uploaded official logo file to:")
        print(f"  {os.path.abspath(logo_path)}")
        print("Then, re-run this processing script.")
        print("==============================================================================")
        return

    print(f"Loading official brand assets from: {logo_path}...")
    try:
        with Image.open(logo_path) as img:
            width, height = img.size
            print(f"Dimensions detected: {width}px x {height}px")

            # In the official logo layout, the "GS" monogram resides on the left
            # as a square. We will crop the square portion from x=0 to x=height. [1]
            crop_box = (0, 0, height, height)
            print(f"Extracting 'GS' monogram brand mark using crop bounding coordinates: {crop_box}...")
            
            monogram = img.crop(crop_box)

            # Compile into multi-size ICO structure [1]
            ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            print(f"Resizing and compiling multi-size ICO targets: {ico_sizes}...")
            
            monogram.save(favicon_path, format="ICO", sizes=ico_sizes)
            print(f"✓ Brand Favicon compiled successfully on disk: {favicon_path}")

    except Exception as e:
        print(f"An error occurred during image processing: {e}")


if __name__ == "__main__":
    process_logo_to_favicon()
    