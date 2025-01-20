import cv2
import time
from ultralytics import YOLO

# 初始化 YOLO 模型
yolo_model = YOLO('yolov8n.pt')

# 等待區的區域座標（畫面中設定的矩形區域）
WAITING_ZONE = [(10, 10), (630, 470)]

# 紅綠燈狀態模擬
RED_LIGHT_TIME = 5  # 紅燈時間（秒）
DETECTION_TIME = 2   # 行人進入等待區後轉綠燈的時間（秒）

# 初始化攝影機
cap = cv2.VideoCapture(0)

def detect_objects(frame, model, classes):
    """使用 YOLO 模型偵測特定類別物件。"""
    results = model.predict(frame)
    detections = results[0].boxes if results else None
    objects = []
    if detections is not None:
        for box in detections:
            cls = int(box.cls[0])
            if cls in classes:
                x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                objects.append((cls, x_min, y_min, x_max, y_max, conf))
    return objects

def draw_bounding_boxes(frame, objects, color_map):
    """在影像上繪製邊框。"""
    for obj in objects:
        cls, x_min, y_min, x_max, y_max, conf = obj
        color = color_map.get(cls, (255, 255, 255))
        label = f"{'person' if cls == 0 else 'car'} {conf:.2f}"
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def check_pedestrian_in_zone(objects, zone):
    """檢查行人是否在等待區內。"""
    for obj in objects:
        cls, x_min, y_min, x_max, y_max, conf = obj
        if cls == 0:  # 類別 0 表示行人
            x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
            if zone[0][0] < x_center < zone[1][0] and zone[0][1] < y_center < zone[1][1]:
                return True
    return False

def traffic_light_control(state, pedestrian_detected, detection_start_time, pedestrian_in_zone, start_time):
    """模擬紅綠燈控制邏輯。"""
    if state == "RED":
        if pedestrian_detected:
            if detection_start_time is None:
                detection_start_time = time.time()
            elif time.time() - detection_start_time >= DETECTION_TIME:
                state = "GREEN"
                pedestrian_in_zone = True
                detection_start_time = None
        else:
            detection_start_time = None
    elif state == "GREEN":
        if not pedestrian_detected:
            if pedestrian_in_zone:
                start_time = time.time()
                pedestrian_in_zone = False
        else:
            start_time = time.time()
            pedestrian_in_zone = True

        if time.time() - start_time >= RED_LIGHT_TIME and not pedestrian_detected:
            state = "RED"

    return state, detection_start_time, pedestrian_in_zone, start_time

def main():
    state = "RED"
    start_time = time.time()
    detection_start_time = None
    pedestrian_in_zone = False

    color_map = {0: (0, 255, 0), 2: (255, 0, 0)}  # 行人: 綠色, 車輛: 藍色

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        objects = detect_objects(frame, yolo_model, classes=[0, 2])
        draw_bounding_boxes(frame, objects, color_map)

        pedestrian_detected = check_pedestrian_in_zone(objects, WAITING_ZONE)
        state, detection_start_time, pedestrian_in_zone, start_time = traffic_light_control(
            state, pedestrian_detected, detection_start_time, pedestrian_in_zone, start_time
        )

        # 繪製等待區
        cv2.rectangle(frame, WAITING_ZONE[0], WAITING_ZONE[1], (0, 0, 255) if state == "RED" else (0, 255, 0), 2)

        # 顯示紅綠燈狀態
        time_left = int(DETECTION_TIME - (time.time() - detection_start_time)) if state == "RED" and detection_start_time else 0
        if state == "RED":
            cv2.putText(frame, f"Light: RED", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if detection_start_time:
                cv2.putText(frame, f"Switching in: {time_left}s", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        elif state == "GREEN":
            cv2.putText(frame, f"Light: GREEN", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if not pedestrian_detected:
                time_left = int(RED_LIGHT_TIME - (time.time() - start_time))
                cv2.putText(frame, f"Switching to RED in: {time_left}s", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 顯示畫面
        cv2.imshow("Pedestrian and Vehicle Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
