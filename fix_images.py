"""Fix the iCCP warning by stripping bad sRGB profiles from all PNGs."""
from PIL import Image
import os

def strip_profile(filepath):
    """Re-save the image without the ICC profile."""
    try:
        img = Image.open(filepath)
        # Re-save without the ICC profile
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(filepath)
        return True
    except Exception as e:
        print(f"Failed on {filepath}: {e}")
        return False

count = 0
for root, dirs, files in os.walk("images"):
    for f in files:
        if f.lower().endswith(".png"):
            path = os.path.join(root, f)
            if strip_profile(path):
                count += 1

print(f"Fixed {count} PNG files.")