import torch
import torch.nn.functional as F
from torch import nn

from position_encoding import position_encoding

class NeRF(nn.Module):
  def __init__(self, position_enc_dim = 63, view_enc_dim = 27, hidden_dim = 256):
    super().__init__()
    # 1st layer, from position encoding to the linear
    self.linear1 = nn.Sequential(nn.Linear(position_enc_dim, hidden_dim), nn.ReLU())

    # followed by 4 linear layers
    self.pre_skip_layers = nn.Sequential()
    for _ in range(4):
      self.pre_skip_layers.append(nn.Linear(hidden_dim, hidden_dim))
      self.pre_skip_layers.append(nn.ReLU())

    # skip connection: position encoding + linear layer
    self.skip_connection_layer = nn.Sequential(nn.Linear(position_enc_dim + hidden_dim, hidden_dim), nn.ReLU())

    # followed by 2 linear layers
    self.post_skip_layers = nn.Sequential()
    for _ in range(2):
      self.post_skip_layers.append(nn.Linear(hidden_dim, hidden_dim))
      self.post_skip_layers.append(nn.ReLU())

    # density layer, with output size 1
    self.density_layer = nn.Sequential(nn.Linear(hidden_dim, 1), nn.ReLU())

    # another linear layer without ReLU activation function
    self.linear2 = nn.Linear(hidden_dim, hidden_dim)

    # skip connection 2: position encoding of size 27 + linear layer, reduce output hidden layer size
    self.skip_connection_layer_2 = nn.Sequential(nn.Linear(view_enc_dim + hidden_dim, hidden_dim//2), nn.ReLU())

    # color layer: with output size 3, and sigmoid activation function
    self.color_linear = nn.Sequential(nn.Linear(hidden_dim//2, 3), nn.Sigmoid())

  def forward(self, cam_coord):
    # Extract pos and view dirs
    rotation = cam_coord[..., :3] # The Rotation Matrix of the Camera, 3x3 shape
    # Shape: [Num_of_images, 4, 3]

    view_dirs = cam_coord[..., 3:]  # The Position Vector of the Camera, 3x1 shape
    # Shape: [Num_of_images, 1, 27]

    # Encode into low and high frequency
    encoded_rotation = position_encoding(rotation, L_embeds=10)
    # Shape: [Num_of_images, 4, 3 + 3*2*L_embeds], (63)

    encoded_view_dirs = position_encoding(view_dirs, L_embeds=4)
    # Shape: [Num_of_images, 4, 9] # [50, 4, 9]

    # pass trough the first linear layer
    # Input: [Num_of_images, 4, 3 + 3*2*L_embeds]
    x = self.linear1(encoded_rotation)
    # Output: [Num_of_images, 4, hidden_dim]

    # followed by 4 linear layers
    x = self.pre_skip_layers(x)
    # Output: [Num_of_images, 4, hidden_dim]

    # SKip connection for rotation encoding with x
    x = torch.cat([x, encoded_rotation], dim=-1)
    # Output: [Num_of_images, 4, (3 + 3*2*L_embeds) + hidden_dim] # 256+63=319

    x = self.skip_connection_layer(x)
    # Output: [Num_of_images, 4, hidden_dim]

    # followed by 2 more linear layers after the 1st skip connection
    x = self.post_skip_layers(x)
    # Output: [Num_of_images, 4, hidden_dim]

    # density layer gives the density value.
    sigma = self.density_layer(x)
    # Output: [Num_of_images, 4, 1]

    # Another linear layer
    x = self.linear2(x)
    # Output: [Num_of_images, 4, hidden_dim]

    # 2nd skip connection, this time from translation vector, encoded_view_dirs
    x = torch.cat([x, encoded_view_dirs], dim=-1)
    # Output: [Num_of_images, 4, 265] # [Num_of_images, 4, hidden_dim] + [Num_of_images, 4, 9] = [Num_of_images, 4, 265]

    x = self.skip_connection_layer_2(x)
    # Shape: [Num_of_images, 4, hidden_dim//2])

    # color prediction
    rgb = self.color_linear(x)
    # Output: [Num_of_images, 4, 3]

    return torch.cat([sigma, rgb], dim=-1)