using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class nerfDataCollection : MonoBehaviour
{

    int currentFrame = 0;

    public Camera cam;

    private Matrix4x4 m;
    public Matrix4x4 c2w;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (currentFrame % 5 == 0)
        {
            // capture the screen

            // get the camera transform - position and rotation
            m = cam.cameraToWorldMatrix;
            c2w = m.inverse;

            for (int i = 0; i < 4; i++) {
                c2w[i, 1] *= -1; // Flip Y
                c2w[i, 2] *= -1; // Flip Z
            }



        }


    }
}
