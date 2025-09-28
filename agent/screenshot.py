import base64
import io
from PIL import Image

try:
    from Quartz import (
        CGWindowListCreateImage,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
        CGRectInfinite,
    )
    from Quartz.CoreGraphics import (
        CGImageGetWidth,
        CGImageGetHeight,
        CGDataProviderCopyData,
        CGImageGetDataProvider,
    )
    _QUARTZ_AVAILABLE = True
except ImportError:
    _QUARTZ_AVAILABLE = False

def add_grid_overlay(image, grid_size=20):
    """Add a high-precision coordinate grid overlay to the image for ultra-precise clicking."""
    from PIL import ImageDraw, ImageFont
    
    # Create a copy to draw on
    img_with_grid = image.copy()
    draw = ImageDraw.Draw(img_with_grid)
    
    width, height = image.size
    
    # Different line colors for major and minor grid lines
    major_grid_color = (255, 0, 0, 180)  # Red for major lines
    minor_grid_color = (255, 100, 100, 120)  # Light red for minor lines
    
    # Calculate grid spacing
    grid_width = width // grid_size
    grid_height = height // grid_size
    
    # Draw minor grid lines (thinner, every line)
    for i in range(grid_size + 1):
        x = i * grid_width
        line_width = 2 if i % 5 == 0 else 1  # Thicker every 5th line
        color = major_grid_color if i % 5 == 0 else minor_grid_color
        draw.line([(x, 0), (x, height)], fill=color, width=line_width)
    
    for i in range(grid_size + 1):
        y = i * grid_height
        line_width = 2 if i % 5 == 0 else 1  # Thicker every 5th line
        color = major_grid_color if i % 5 == 0 else minor_grid_color
        draw.line([(0, y), (width, y)], fill=color, width=line_width)
    
    # Add coordinate labels with higher precision
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
    except:
        font = ImageFont.load_default()
    
    # Add precise coordinate labels (every 5th line to avoid clutter)
    for i in range(0, grid_size + 1, 5):
        for j in range(0, grid_size + 1, 5):
            x = i * grid_width
            y = j * grid_height
            
            # Convert to ratio coordinates with higher precision
            ratio_x = round(i / grid_size, 2)  # 2 decimal places
            ratio_y = round(j / grid_size, 2)
            
            # Draw coordinate label with precise values
            label = f"({ratio_x:.2f},{ratio_y:.2f})"
            
            # Add background rectangle for text readability
            bbox = draw.textbbox((x + 2, y + 2), label, font=font)
            draw.rectangle(bbox, fill=(255, 255, 255, 220))  # White background
            draw.text((x + 2, y + 2), label, fill=(0, 0, 0), font=font)
    
    # Add crosshairs at center points for extra precision
    crosshair_color = (0, 255, 0, 200)  # Green crosshairs
    for i in range(1, grid_size, 2):  # Odd positions for center points
        for j in range(1, grid_size, 2):
            x = i * grid_width
            y = j * grid_height
            
            # Draw small crosshair
            draw.line([(x-3, y), (x+3, y)], fill=crosshair_color, width=2)
            draw.line([(x, y-3), (x, y+3)], fill=crosshair_color, width=2)
    
    return img_with_grid

def capture_to_bytes(add_grid=True):
    """Captures the screen using macOS screencapture command and returns base64 encoded JPEG bytes."""
    import subprocess
    import tempfile
    import os
    
    try:
        # Create a temporary file for the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Use macOS screencapture command to capture the main display
        result = subprocess.run([
            'screencapture', 
            '-x',  # Don't play camera sound
            '-t', 'png',  # PNG format
            temp_path
        ], capture_output=True, check=True)
        
        # Read the screenshot file
        with open(temp_path, 'rb') as f:
            png_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Convert PNG to JPEG using PIL
        from PIL import Image
        import io
        
        # Open PNG data
        png_image = Image.open(io.BytesIO(png_data))
        
        # Convert to RGB (remove alpha channel if present)
        if png_image.mode in ('RGBA', 'LA'):
            rgb_image = Image.new('RGB', png_image.size, (255, 255, 255))
            rgb_image.paste(png_image, mask=png_image.split()[-1] if png_image.mode == 'RGBA' else None)
        else:
            rgb_image = png_image.convert('RGB')
        
        # Add grid overlay for precise clicking
        if add_grid:
            rgb_image = add_grid_overlay(rgb_image, grid_size=20)
        
        # Convert to JPEG bytes
        img_byte_arr = io.BytesIO()
        rgb_image.save(img_byte_arr, format="JPEG", quality=85)
        img_bytes = img_byte_arr.getvalue()
        
        # Return base64 encoded
        return base64.b64encode(img_bytes).decode('utf-8')
        
    except subprocess.CalledProcessError as e:
        print(f"screencapture command failed: {e}")
        return None
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None