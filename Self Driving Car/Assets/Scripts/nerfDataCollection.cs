using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class nerfDataCollection : MonoBehaviour
{

    // camera intrinsic properties.
    public Camera cam;
    public Matrix4x4 m;
    private double camera_angle_x;
    
    public float maxDistance = 100.0f; // the maximum distance to record data.
    public float distanceThreshold = 1.0f; // the distance threshold to capture every x meters

    private Vector3 lastPosition; // to store the last position of the camera/car
    private float totalDistance = 0.0f; // to keep track of the total distance traveled by the camera/car, we will stop the data collection after we reach the max distance.
    private float steps = 0.0f;
    private int frameCount = 0;

    // Data Collector
    private NeRFData data = new NeRFData();

    // Start is called before the first frame update
    void Start()
    {
        this.cam = GetComponent<Camera>();
        // last known position of the camera/car
        lastPosition = transform.position;
        camera_angle_x = CameraAngle();

        data.camera_angle_x = camera_angle_x;

        StartCoroutine(ProcessData());
    }

    // Update is called once per frame
    void Update()
    {
        
        steps = Vector3.Distance(transform.position, lastPosition);
        if ( steps >= distanceThreshold && totalDistance < maxDistance)
        {
            StartCoroutine(ProcessData());

            // the last known position of the camera/car will get updated after we capture the data, so we can measure the distance traveled in the next frame.
            lastPosition = transform.position;
            // total distance travlled so far by the camera/car, we can use this to stop the data collection after we reach the max distance.
            totalDistance += steps;
        }
        
        if (totalDistance >= maxDistance)
        {
            Debug.Log("Max distance reached, stopping data collection.");
            SaveData();
        } 
    }

    IEnumerator ProcessData()
    {
        yield return new WaitForEndOfFrame();

        // capture the game view and save it to the specified folder.
        string frame_name = GameViewCapture();

        // capture the camera's world matrix and flip the Y and Z axis to match the nerf format.
        m = cam.cameraToWorldMatrix;
        
        // flip the value of Y to face it downwords -Y axis.
        // flip the value of Z to face it backwards -Z axis.
        Vector4 up_y = m.GetColumn(1);
        Vector4 forward_z = m.GetColumn(2);
        m.SetColumn(1, -up_y);
        m.SetColumn(2, -forward_z);
        //nerfMatrix = FlipMatrix(m)

        NeRFFrame frame = new NeRFFrame{frame_name=frame_name, camera_to_world_matrix=m};
        data.frames.Add(frame);

        frameCount++;
    }

    public string GameViewCapture()
    {
        string folderPath = "D:/ML/Self Driving Car/self_driving_car/Self-Driving-Car-Python/driving_data/Screenshots/"; // the path of your project folder

        //if (!System.IO.Directory.Exists(folderPath)) // if this path does not exist yet
        //    System.IO.Directory.CreateDirectory(folderPath);  // it will get created
        
        string screenshotName = $"frame_{frameCount:D4}.png"; // frame_0001.png 
        ScreenCapture.CaptureScreenshot(System.IO.Path.Combine(folderPath, screenshotName),2); // takes the sceenshot, the "2" is for the scaled resolution, you can put this to 600 but it will take really long to scale the image up
        //Debug.Log(folderPath + screenshotName);

        return screenshotName;
    }

    public void SaveData()
    {
        // Save the json file
        // Every row should contain the frame name and the corresponding camera transform matrix.
        string jsonPath = "D:/ML/Self Driving Car/self_driving_car/Self-Driving-Car-Python/driving_data/transforms.json";
        string json = JsonUtility.ToJson(data, true);
        File.WriteAllText(jsonPath, json);
        Debug.Log("100 Meters reached! Data Saved.");
    }

    public double CameraAngle()
    {
        // Horizontal Field of View in radians.
        float fov = this.cam.fieldOfView;
        double camera_angle_x = fov * (Math.PI / 180); // convert to radians
        return camera_angle_x;
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
