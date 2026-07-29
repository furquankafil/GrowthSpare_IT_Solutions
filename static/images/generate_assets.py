"""
Corporate Asset Generator for GrowthSpare IT Solutions.
Programmatically draws and writes the official corporate landscape logo
and standard multi-size browser favicon directly to disk.

Execution:
1. Ensure the virtual environment is active and Pillow is installed:
   pip install Pillow
2. Run this script from the project root:
   python generate_assets.py
"""

import os
import math
from PIL import Image, ImageDraw


def create_branding_icon(size=512):
    """
    Draws the official GrowthSpare brand mark:
    - Symmetrical 12-tooth industrial gear (Dark Navy Blue, #0F172A)
    - Ascending trendline with circular nodes and an upward-pointing arrow
      (Primary Blue #2563EB and vibrant Green/Cyan Accent #06B6D4)
    """
    # Create transparent canvas
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    
    # 1. Color Palettes
    color_navy = (15, 23, 42, 255)       # #0F172A
    color_blue = (37, 99, 235, 255)       # #2563EB
    color_accent = (6, 182, 212, 255)     # #06B6D4
    color_green = (34, 197, 94, 255)      # #22C55E
    color_silver = (226, 232, 240, 255)   # #E2E8F0

    # 2. Draw Symmetrical Gear (representing software, structure, and CRM/ERP engines)
    outer_r = size * 0.35
    inner_r = size * 0.25
    
    # Draw outer base circle
    draw.ellipse(
        [center - outer_r, center - outer_r, center + outer_r, center + outer_r],
        fill=color_navy
    )
    
    # Calculate and draw 12 gear teeth symmetrically
    num_teeth = 12
    for i in range(num_teeth):
        angle = (2 * math.pi / num_teeth) * i
        tooth_pts = []
        # Draw trapezoidal teeth projecting outwards
        for offset_angle, r_val in [(-0.1, outer_r), (-0.06, outer_r * 1.15), (0.06, outer_r * 1.15), (0.1, outer_r)]:
            x = center + r_val * math.cos(angle + offset_angle)
            y = center + r_val * math.sin(angle + offset_angle)
            tooth_pts.append((x, y))
        draw.polygon(tooth_pts, fill=color_navy)

    # Cut out hollow inner ring
    draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        fill=(0, 0, 0, 0)
    )
    
    # Draw metallic internal accent track
    track_width = max(2, int(size * 0.03))
    draw.arc(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        start=0, end=360, fill=color_silver, width=track_width
    )

    # 3. Draw Ascending Trendline Arrow (representing organic growth and scaling solutions)
    nodes = [
        (center - size * 0.22, center + size * 0.12),
        (center - size * 0.07, center - size * 0.03),
        (center + size * 0.08, center + size * 0.03),
        (center + size * 0.26, center - size * 0.22)
    ]
    
    # Draw connection lines between nodes
    line_width = max(3, int(size * 0.04))
    for k in range(len(nodes) - 1):
        draw.line([nodes[k], nodes[k+1]], fill=color_blue, width=line_width)
        # Symmetrical nodes joint connectors
        node_radius = line_width
        draw.ellipse(
            [nodes[k][0] - node_radius, nodes[k][1] - node_radius, nodes[k][0] + node_radius, nodes[k][1] + node_radius],
            fill=color_accent
        )
        
    # Draw sharp, rising arrow head at final node tip pointing top-right
    arrow_size = size * 0.11
    arrow_tip = nodes[-1]
    arrow_points = [
        arrow_tip,
        (arrow_tip[0] - arrow_size * 0.2, arrow_tip[1] + arrow_size * 0.9),
        (arrow_tip[0] - arrow_size * 0.9, arrow_tip[1] + arrow_size * 0.2)
    ]
    draw.polygon(arrow_points, fill=color_green)
    
    return img


def generate_assets():
    """Generates and writes corporate PNG and ICO assets to static directories."""
    print("Initializing corporate assets compilation...")

    # Set up directory paths
    target_dir = "static/images"
    os.makedirs(target_dir, exist_ok=True)
    
    logo_path = os.path.join(target_dir, "logo.png")
    favicon_path = os.path.join(target_dir, "favicon.ico")

    # Draw master high-res icon
    master_icon = create_branding_icon(1024)

    # 1. Create Landscape Logo (1200 x 400)
    canvas_w, canvas_h = 1200, 400
    logo_canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))
    
    # Resize and place brand icon left-aligned
    icon_size = 280
    brand_icon_resized = master_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    logo_canvas.paste(brand_icon_resized, (60, (canvas_h - icon_size) // 2), brand_icon_resized)
    
    # Draw geometric typography structures
    draw = ImageDraw.Draw(logo_canvas)
    
    # Hex: #0F172A (Navy) and #64748B (Slate)
    navy_color = (15, 23, 42, 255)
    slate_color = (100, 116, 139, 255)
    
    # Programmatic structural rendering of brand name text layers
    # Enforces standard fallback text metrics if system font paths are unmapped
    draw.text((380, 105), "GrowthSpare", fill=navy_color, font_size=100)
    draw.text((385, 220), "IT SOLUTIONS", fill=slate_color, font_size=42)
    
    logo_canvas.save(logo_path, "PNG")
    print(f"-> Successfully saved: {logo_path}")

    # 2. Create favicon.ico with multi-size standards
    fav_icon = create_branding_icon(256)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    fav_icon.save(favicon_path, format="ICO", sizes=sizes)
    print(f"-> Successfully saved: {favicon_path}")
    
    print("Corporate assets generation completed successfully.")


if __name__ == "__main__":
    generate_assets()