import json
import numpy as np

def load_nerf_poses_from_keys(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    all_poses = []
    
    for frame in data['frames']:
        m = frame['camera_to_world_matrix']
        
        # Manually construct the 4x4 matrix from keys
        matrix = [
            [m['e00'], m['e01'], m['e02'], m['e03']],
            [m['e10'], m['e11'], m['e12'], m['e13']],
            [m['e20'], m['e21'], m['e22'], m['e23']],
            [m['e30'], m['e31'], m['e32'], m['e33']]
        ]
        all_poses.append(matrix)
    
    # Convert to (N, 4, 4) numpy array
    return np.array(all_poses, dtype=np.float32)

# Usage
poses = load_nerf_poses_from_keys('D:/ML/Self Driving Car/self_driving_car/Self-Driving-Car-Python/driving_data/transforms_1st_lane.json')

print(f"Batch Shape: {poses.shape}")
print("Example Matrix (Frame 0):\n", poses[0])