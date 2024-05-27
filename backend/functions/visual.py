import cv2
import numpy as np

def calculate_video_features(video_file):

    cap = cv2.VideoCapture(video_file)
    
    total_saturation = 0
    frame_count = 0
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv[:,:,1]) / 255.0
        total_saturation += saturation
        frame_count += 1
    
    average_saturation = total_saturation / frame_count if frame_count > 0 else 0
    
    return {
        'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
        'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
        'frame_rate': cap.get(cv2.CAP_PROP_FPS),
        'average_saturation': average_saturation
    }