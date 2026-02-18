from PIL import ImageGrab
import numpy as np
import sys

# Optional: read bbox from arguments
if len(sys.argv) == 5:
    left, top, right, bottom = map(int, sys.argv[1:])
else:
    # Default capture region
    left, top, right, bottom = 0, 120, 750, 540

# Grab screen
img = ImageGrab.grab(bbox=(left, top, right, bottom))

# Convert to numpy array
arr = np.array(img)

# Save to stdout as bytes
arr.tofile(sys.stdout.buffer)
