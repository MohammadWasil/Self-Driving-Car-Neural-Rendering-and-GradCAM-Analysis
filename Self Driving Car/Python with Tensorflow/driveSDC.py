import socket

from tensorflow.keras.models import load_model


from PIL import ImageGrab
import numpy as np
import cv2
import os

from grad_cam import compute_gradcam_regression

#Load the model.
model = load_model("D:\ML\Self Driving Car\self_driving_car\Self-Driving-Car-Python\Self Driving Car\Python with Tensorflow\Best Models/data-003.h5") 	# Directory to load the model


# Socket Tcp Connection.
host = "127.0.0.1"
#host = os.popen("grep nameserver /etc/resolv.conf | cut -d' ' -f2").read().strip()
#host = "192.168.0.233"
print(host)
port = 25001            # Port number
#data = "1,1,11"         # Data to be send
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # TCP connection
print("starting connection")
try:
    sock.connect((host, port))                  #To connect ot the given port.
    print("Connected")
    
except:
    print("Might happen socket is closed!")
#######

def send_data(steering_angle, throttle):
    data_01 = str(steering_angle)
    data_02 = str(throttle)
    data = data_01 + ',' + data_02
    sock.sendall(data.encode("utf-8"))          # To send the data

steeringAngleList = []
velocityList = []
throttleList = []

steeringAngle = 0
velocity = 0
throttle = 0

arr1=[]
arr2=[]
arr3=[]
splitted_data = []
reply=[]
def socketConnection():
    global globalsteeringAngle
    global velocity
    global throttle
    try:
        #data = "1,0"
        
        reply = sock.recv(2048).decode("utf-8")    # To receive the data
        #######send_data(reply)
        #print("Actual data received is: ", reply)
       
        splitted_data = reply.split(',')
        #print("after splitting the data: ", splitted_data)
        arr1.append(splitted_data[0])
        arr2.append(splitted_data[1])
        arr3.append(splitted_data[2])
        
        steeringAngle = float(splitted_data[0])
        velocity = float(splitted_data[1])
        throttle = float(splitted_data[2])
        
    except:
        print("Exception")
    
    steeringAngleList = np.array(arr1) 
    velocityList = np.array(arr2)
    throttleList = np.array(arr3)

    return steeringAngleList, velocityList, throttleList, steeringAngle, velocity, throttle


filename = r"D:\ML\Self Driving Car\self_driving_car\Self-Driving-Car-Python\driving_data\Drive_SDC_3_lane_way.csv" 	#Directory to save your current Data in a csv file.

def csv_file(steer_Angle, velocity, throttle):
    
    #print("Writing to csv file!")
    f = open(filename, "w")
    f.write("{},{},{}\n".format("Steerring Angle", "Current Velocity", "Throttle"))
    
    for x in zip( steer_Angle, velocity, throttle):
        f.write("{},{},{}\n".format(x[0], x[1], x[2]))
    
    f.close()

#############################   
MAX_SPEED = 25
MIN_SPEED = 10
speed_limit = MAX_SPEED

def preprocess(image):
    return cv2.resize(image, (200, 66), cv2.INTER_AREA)

def image_process(image):
    image = np.asarray(image)       # from PIL image to numpy array
    image = preprocess(image)       # apply the preprocessing
    image = np.array([image])       # the model expects 4D array
    return image

def drive(image, steering_angle, velocity, throttle):

    try:
        steering_angle = float(model.predict(image, batch_size=1))
        steering_angle = (steering_angle/10)
        global speed_limit
        if velocity > speed_limit:
            speed_limit = MIN_SPEED  # slow down
        else:
            speed_limit = MAX_SPEED
        throttle = 1.0 - steering_angle**2 - (velocity/speed_limit)**2

        print('{} {} {}'.format(steering_angle, throttle, velocity))
        steering_angle = (steering_angle*10)
        send_data(steering_angle, throttle)
        
    except Exception as e:
        print("Exception Occured", e)

    return steering_angle

def resize_heatmap_to_image(heatmap, original_image):
    """
    Resize a Grad-CAM heatmap to match the original image size.

    Args:
        heatmap: 2D numpy array, shape = (conv_height, conv_width)
        original_image: 3D numpy array, shape = (H, W, C)

    Returns:
        heatmap_resized: 2D numpy array, shape = (H, W)
    """
    H, W = original_image.shape[:2]

    # Resize heatmap to match original image
    heatmap_resized = cv2.resize(heatmap, (W, H), interpolation=cv2.INTER_LINEAR)

    # Optional: normalize to 0-1
    heatmap_resized = (heatmap_resized - heatmap_resized.min()) / (heatmap_resized.max() - heatmap_resized.min() + 1e-8)
    heatmap_resized = np.uint8(255 * heatmap_resized)
    return heatmap_resized

def overlay_heatmap(img, heatmap, alpha=0.5):
    """
    img: Original image (Numpy array)
    heatmap: 2D heatmap (Numpy array, values 0 to 1)
    alpha: Transparency (0.5 means 50% image, 50% heatmap)
    """
    # 1. Resize heatmap to match original image size
    #heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))

    # 2. Convert heatmap to 0-255 range (uint8)
    heatmap_255 = np.uint8(255 * heatmap)

    # 3. Apply a ColorMap (JET is standard for "hot/cold" visuals)
    heatmap_color = cv2.applyColorMap(heatmap_255, cv2.COLORMAP_JET)
    #print("Original image size: ", img.shape)
    #print("Heatmap image size: ", heatmap_color.shape)
    #sys.stdout.flush() # Forces the print to appear NOW

    # 4. Ensure dtypes match (OpenCV blending needs same type)
    #if img.dtype != np.uint8:
    #    img = np.uint8(img)

    # 4. Blend the two images
    # formula: result = (img * (1-alpha)) + (heatmap * alpha)
    #overlayed_img = cv2.addWeighted(img[0], 1 - alpha, heatmap_color, alpha, 0) # img: shape (1, H, W, Channel)
    overlayed_img = cv2.addWeighted(img, 1 - alpha, heatmap_color, alpha, 0) # img: shape (H, W, Channel)

    return overlayed_img


num = 0  
path = r"D:\ML\Self Driving Car\self_driving_car\Self-Driving-Car-Python\driving_data\Drive SDC 3-way lane"         # Destination/path to which all the current images will be saved 
heatmap_path = r"D:\ML\Self Driving Car\self_driving_car\Self-Driving-Car-Python\driving_data\Drive_SDC_heatmap_3-way_lane_out_of_domain"         # Destination/path to which all the current images will be saved 
while (True):
    num = num + 1
    imageName = 'Wasil'+ str(num) + '.png'      # Name of the images.
    #collecting current data
    strAngl, vlcty, thrttl, steeringAngle, velocity, throttle  = socketConnection()
    image_ori = np.array(ImageGrab.grab(bbox=(0, 120, 750, 540)))          # Taking the screebshot and adding in the array
    
    #csv_file(strAngl, vlcty, thrttl)
    #cv2.imwrite(os.path.join(path, imageName), image_ori)                                       # Trying to save the image in the exact same directory.
    
    image = image_process(image_ori)      # Preprocessing the image.

    steering_angle = drive(image, steeringAngle, velocity, throttle)

    # computer gradient cam heatmap
    #heatmap = compute_gradcam_regression(model, image, steering_angle) # in numpy array format.
    #heatmap_resized = resize_heatmap_to_image(heatmap, image_ori)
    #print(image.shape, heatmap.shape)
    #result = overlay_heatmap(image_ori, heatmap_resized)

    #imageName = 'sdc_heatmap_original_'+ str(num) + '.png'
    #cv2.imwrite(os.path.join(heatmap_path, imageName), result)

"""
### NOTE: divide steering angle by 10.
"""