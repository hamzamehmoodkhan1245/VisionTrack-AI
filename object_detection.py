import cv2
import numpy as np
import os

class ObjectDetection:
    def __init__(self):
        print("Loading Object Detection")
        print("Running opencv dnn with YOLOv4")

        # Paths to YOLOv4 config and weights
        model_dir = os.path.join(os.path.dirname(__file__), 'dnn_model')
        weights_path = os.path.join(model_dir, 'yolov4.weights')
        cfg_path = os.path.join(model_dir, 'yolov4.cfg')

        # Load the network
        self.net = cv2.dnn.readNet(weights_path, cfg_path)

        # ⚠️ Force CPU usage (no GPU/CUDA)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Load class names from coco.names (optional, can be added later)
        self.classes = []
        coco_path = os.path.join(model_dir, 'coco.names')
        if os.path.exists(coco_path):
            with open(coco_path, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

        # Set parameters
        self.confThreshold = 0.5
        self.nmsThreshold = 0.3

        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]

    def detect(self, frame):
        height, width, _ = frame.shape

        # Convert frame to blob
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.confThreshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        final_boxes = [boxes[i] for i in indices.flatten()]
        final_class_ids = [class_ids[i] for i in indices.flatten()]
        final_confidences = [confidences[i] for i in indices.flatten()]

        return final_class_ids, final_confidences, final_boxes
