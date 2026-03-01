import torch
import torch.nn.functional as F

from model import NeRF

def test_nerf_flow():

    # Dummy Data
    num_samples = 4 # ray samples originating from every pixel in the image, each sample has 3D coordinates and view direction
                    # Taken 4 for testing here, but in practice, this can be much larger (eg., 1024 or more)
    pts = torch.randn(num_samples, 3)          # Spatial points
    dirs = torch.randn(num_samples, 3)         # View directions
    dirs = F.normalize(dirs, dim=-1)                       # Normalize to unit vectors
    
    dummy_input = torch.cat([pts, dirs], dim=-1)           # Shape: [50, 4, 6]
    
    print(f"Testing with input shape: {dummy_input.shape} \n")
    model = NeRF()
    
    # Forward Pass
    try:
        output = model(dummy_input)
        
        assert output.shape == torch.Size([4, 4]) 
        print("Forward pass: Successful.")
        
        sigma = output[..., 0]
        rgb = output[..., 1:]
        print(f"Density (sigma) range: [{sigma.min():.4f}, {sigma.max():.4f}]")
        print(f"Color (RGB) range:    [{rgb.min():.4f}, {rgb.max():.4f}]")

    except Exception as e:
        print(f"Forward pass: FAILED")
        print(f"Error: {e}")