using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class networkTester : MonoBehaviour
{
    Thread thread;
    TcpListener listener;

    void Start()
    {
        thread = new Thread(Run);
        thread.IsBackground = true;
        thread.Start();
    }

    void Run()
    {
        listener = new TcpListener(System.Net.IPAddress.Any, 25001);
        
        listener.Start();
        Debug.Log("SERVER LISTENING");

        var client = listener.AcceptTcpClient();
        Debug.Log("CLIENT CONNECTED");

        var stream = client.GetStream();
        byte[] buffer = new byte[1024];

        while (true)
        {
            int len = stream.Read(buffer, 0, buffer.Length);
            if (len > 0)
            {
                string msg = Encoding.UTF8.GetString(buffer, 0, len);
                Debug.Log("RECEIVED: " + msg);
            }
        }
    }

    void OnApplicationQuit()
    {
        listener?.Stop();
        thread?.Abort();
    }
}
