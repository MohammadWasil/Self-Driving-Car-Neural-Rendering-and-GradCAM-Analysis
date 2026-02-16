import json
import os
import numpy as np
from PIL import Image

def load_images_to_npy(json_path, image_folder, target_h=100):
    """
    json_path: path to your transforms.json
    image_folder: folder where the .png files are stored
    target_size: (Height, Width) to ensure consistency
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    image_list = []
    
    for frame in data['frames']:
        # Get the filename from the JSON
        img_name = frame['frame_name']
        img_path = os.path.join(image_folder, img_name)
        
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB')
            
            # Calculate width to maintain aspect ratio
            # Example: 1920/1080 * 100 = 177px wide
            aspect_ratio = img.width / img.height
            target_w = int(target_h * aspect_ratio)
            
            # Use Lanczos or Bilinear for high-quality downscaling
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            #image_list.append(np.array(img))
            image_list.append(np.array(img).astype(np.float32) / 255.0)
        else:
            print(f"Warning: {img_path} not found.")

    # Stack into (Batch_Size, H, W, 3)
    batch_images = np.stack(image_list, axis=0)
    return batch_images

# Usage
JSON_FILE = 'D:/ML/Self Driving Car/self_driving_car/Self-Driving-Car-Python/driving_data/transforms_1st_lane.json'
IMG_DIR = 'D:/ML/Self Driving Car/self_driving_car/Self-Driving-Car-Python/driving_data/screenshots_1st_lane/'

image_batch = load_images_to_npy(JSON_FILE, IMG_DIR)

print(f"Image Batch Shape: {image_batch.shape}") # (N, 720, 1280, 3)

# Save as single file
np.save('transforms_1st_lane.npy', image_batch)