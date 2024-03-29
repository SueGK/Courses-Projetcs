# import the necessary packages
import os
import numpy as np
import argparse
import cv2
import matplotlib.pyplot as plt
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# get args and concatenate with current directory
# get current directory
dirname, filename = os.path.split(os.path.abspath(__file__))
prototxt = os.path.join(dirname, "model", args["prototxt"])
model = os.path.join(dirname, "model", args["model"])
image = os.path.join(dirname, "images", args["image"])

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
image = cv2.imread(image)
(h, w) = image.shape[:2]
# preprocess with mean subtraction and normalizing
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, 
	(300, 300), (104.0, 177.0, 123.0), swapRB=True)

# pass the blob through the network and obtain the detections and
# predictions
print("[INFO] computing object detections...")
net.setInput(blob)
detections = net.forward()

# loop over the detections and draw boxes around the detected faces:
for i in range(detections.shape[2]):
	# extract the confidence (i.e., probability) associated with the prediction
	confidence = detections[0, 0, i, 2]

	# filter out weak detections by ensuring the `confidence` is
	# greater than the minimum confidence
	if confidence >= args["confidence"]:
		# compute the (x, y)-coordinates of the bounding box for the
		# object
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h]) # 3-6 contains the coordinate
		(startX, startY, endX, endY) = box.astype("int")

		# draw the bounding box of the face along with the associated
		# probability
		text = f"{(confidence * 100):.2f}%"
		y = startY - 10 if startY - 10 > 10 else startY + 10
		cv2.rectangle(image, 
					  (startX, startY), 
					  (endX, endY),
					  (0, 255, 0), # green rectangle line
					  2) # thickness of lines is 2 px
		cv2.putText(image, text, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.45, color=(0, 255, 0), thickness=2)

# show the output image
cv2.imshow("Output", image)
# display a window for given milliseconds or until any key is pressed
cv2.waitKey(0)
