import torch

def position_encoding(cam_coordinate, L_embeds):
    """
    Positional encoding is used to encode the spatial information of the camera coordinates into a higher-dimensional space.
    
    cam_coordinate is the [x, y, z] coordinate values of the camera.
    gamma(cam_coordinate) = [x, sin(2^0 * pie * cam_coordinate), cos(2^0 * pie * cam_coordinate), sin(2^1 * pie * cam_coordinate), cos(2^1 * pie * cam_coordinate), .....
                sin(2^(L-1) * pie * cam_coordinate), cos(2^(L-1) * pie * cam_coordinate)]
    
    Inputs :
        cam_coordinate : [x, y, z] coordinate values of the camera for a single pixel. 
                        Shape: [total_num_samples , 3] (3 is for x, y, and z coordinates)
                                where, total_num_samples is the total samples along the ray, for every pixel in an image.
        L_embeds : Number of frequency bands to be used for encoding. Higher L_embeds means more high-frequency details can be captured, 
                  but also increases the dimensionality of the encoding.

    Return :
        Shape : [total_num_samples, 3 + (3*2*L_embed)]

    Eg., for L_embed = 10, shape of the positonal encoding will be: [total_num_samples, 63]
    """
    # include original cam_coordinate as well, or else network struggle to learn low frequency function
    encode = [cam_coordinate]
    for i in range(L_embeds):
        for trig_func in [torch.sin, torch.cos]:
            encode.append(trig_func((2.**i)* torch.pi * cam_coordinate))
    return torch.hstack(encode)
