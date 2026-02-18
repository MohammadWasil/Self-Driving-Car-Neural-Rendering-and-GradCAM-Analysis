using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class NeRFFrame
{
    public string frame_name; // the name of the captured frame/screenshot
    public Matrix4x4 camera_to_world_matrix; // the camera's world matrix (extrinsic parameters)
}

[System.Serializable]
public class NeRFData
{
    public double camera_angle_x; // the camera's horizontal field of view (intrinsic parameter)
    public List<NeRFFrame> frames = new List<NeRFFrame>(); // a list of captured frames and their corresponding camera matrices
}
