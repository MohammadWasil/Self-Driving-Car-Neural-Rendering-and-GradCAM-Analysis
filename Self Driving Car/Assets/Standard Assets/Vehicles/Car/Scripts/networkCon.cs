// Server script
// Sends the data to python.

using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using System.Linq;
using UnityStandardAssets.Vehicles.Car;


namespace UnityStandardAssets.Vehicles.Car{
public class networkCon : MonoBehaviour {

	Thread mThread;

	public string connectionIP = "127.0.0.1";		
	public int connectionPort = 25001;

	public CarController carController;
	public float steeringAngle;
	public string steering;

	public float currentVelocity;
	public string velocity;

	public float currentthrottle;
	public string throttle;

	public string combine;

	public float SteeringAngleTest;
	public float ThrottleTest;

	IPAddress localAdd;
	TcpListener listener;
	TcpClient client;

	string message = "Wasil"; 		// The message to send back.

	bool running;

	private void Start()
	{
		ThreadStart ts = new ThreadStart(GetInfo);
		mThread = new Thread(ts);
		mThread.Start();
	}

	private void Update()
	{
		//transform.position = pos;
		steeringAngle = carController.m_SteerAngle;
		currentVelocity = carController.currentVelocity;
		currentthrottle = carController.throttle;

		steering = steeringAngle.ToString ();
		velocity = currentVelocity.ToString ();
		throttle = currentthrottle.ToString ();

		combine = "" + steering + "," + "" + velocity + "," + throttle;
	}

	/*
	public static string GetLocalIPAddress()
	{
		var host = Dns.GetHostEntry(Dns.GetHostName());
		foreach (var ip in host.AddressList)
		{
			if (ip.AddressFamily == AddressFamily.InterNetwork)
			{
				return ip.ToString();
			}
		}
		throw new System.Exception("No network adapters with an IPv4 address in the system!");
	}
	*/

	void GetInfo()
	{
		localAdd = IPAddress.Parse(connectionIP);
		listener = new TcpListener(IPAddress.Any, connectionPort);	// Tcp server
		listener.Start();											

		client = listener.AcceptTcpClient();
		Debug.Log ("Connected");
		running = true;
		while (running)
		{
			Connection();
		}
		listener.Stop();
	}

	void Connection()
	{
		NetworkStream nwStream = client.GetStream();

		byte[] sendData = new byte[4096];
		sendData = Encoding.ASCII.GetBytes (combine);
		nwStream.Write (sendData, 0, sendData.Length);
	

		byte[] buffer = new byte[client.ReceiveBufferSize];
		int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize);
		string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead);

		//nwStream.Write(buffer, 0, bytesRead);
		// Debug.Log (dataReceived);

		getData (dataReceived);

	}

	void getData (string dataReceived)
	{
		string[] values = dataReceived.Split(',');

		SteeringAngleTest = float.Parse(values [0]);
		ThrottleTest = float.Parse(values [1]);
		Debug.Log (SteeringAngleTest + ","+ ThrottleTest);

	}
}
}
