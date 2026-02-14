using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class nerfDataCollection : MonoBehaviour
{

    public Camera cam;

    public Matrix4x4 m;

    // Start is called before the first frame update
    void Start()
    {
    
    }

    // Update is called once per frame
    void Update()
    {
        m = cam.cameraToWorldMatrix;
        
        // flip the value of Y to face it downwords -Y axis.
        // flip the value of Z to face it backwards -Z axis.
        Vector4 up_y = m.GetColumn(1);
        Vector4 forward_z = m.GetColumn(2);
        m.SetColumn(1, -up_y);
        m.SetColumn(2, -forward_z);
        //nerfMatrix = FlipMatrix(m)
    }

    public float[][] FlipMatrix(Matrix4x4 mat){

        float [][] nerfMatrix = new float[4][];

        for(int i =0; i < 4; i++)
        {
            Vector4 row = mat.GetRow(i);
            nerfMatrix[i] = new float [] { row.x, -row.y, -row.z, row.w } ;
        }

        return nerfMatrix;
    }
}
