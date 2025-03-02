import cv2  ## used for reading , resizing and proecessing images
import numpy as np 

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (128, 128))  # Resize for model input
    image = image / 255.0 # Normalize
    return np.expand_dims(image, axis=0)  # Add batch dimension 