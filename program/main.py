import cv2
import time
import numpy as np
import serial
from ultralytics import YOLO

# 初始化 YOLO 模型
yolo_model = YOLO('yolov8l.pt')

# 等待區的區域座標（畫面中設定的矩形區域）
WAITING_ZONE = [(50, 360), (600, 420)]

# 紅綠燈狀態模擬
RED_LIGHT_TIME = 7  # 紅燈時間（秒）
DETECTION_TIME = 3   # 行人進入等待區後轉綠燈的時間（秒）

# 初始化攝影機
cap = cv2.VideoCapture(0)
# 用OBS的虛擬相機，此程式對應路口網址(https://tcnvr3.taichung.gov.tw/983191db)

# 初始化 Arduino 連接
arduino = serial.Serial('COM3', 9600, timeout=1)  # 根據實際連接的 COM 埠號調整


def rotate_frame(frame, angle):
    """將影像以中心為軸旋轉指定角度"""
    (h, w) = frame.shape[:2]  # 獲取影像高度與寬度
    center = (w // 2, h // 2)  # 計算影像中心
    # 獲取旋轉矩陣 (M)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    # 計算旋轉後的邊界大小，避免影像被裁切
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    # 調整旋轉矩陣以考慮新的影像大小
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    # 執行旋轉
    rotated = cv2.warpAffine(frame, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return rotated

def get_state_from_sensor():
    """從 Arduino 接收感測區內是否有人"""
    if arduino.in_waiting > 0:
        try:
            sensor = int(arduino.readline().decode('utf-8').strip())
            return sensor
        except ValueError:
            pass
    return None

def send_light_state_to_arduino(state):
    """當燈號改變時，將狀態字符 ('g' 或 'r') 傳回 Arduino"""
    if state == "GREEN":
        arduino.write(b'g')
    elif state == "RED":
        arduino.write(b'r')

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
    """在影像上繪製邊框，並正確顯示類別標籤。"""
    for obj in objects:
        cls, x_min, y_min, x_max, y_max, conf = obj
        color = color_map.get(cls, (255, 255, 255))  # 根據類別選擇顏色
        # 更新標籤以正確反映類別
        label = f"{'person' if cls == 0 else 'car' if cls == 2 else 'motorcycle' if cls == 3 else 'unknown'} {conf:.2f}"
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)  # 繪製邊框
        cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)  # 繪製標籤

def check_pedestrian_in_zone(objects, zone, sensor):
    """檢查行人是否在等待區內，排除騎機車的行人，並根據距離條件判斷。"""
    if not sensor:
        return False

    motorcycles = [(x_min, y_min, x_max, y_max) for cls, x_min, y_min, x_max, y_max, conf in objects if cls == 3]  # 機車類別為 3
    for obj in objects:
        cls, x_min, y_min, x_max, y_max, conf = obj
        if cls == 0:  # 類別 0 表示行人
            x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
            if zone[0][0] < x_center < zone[1][0] and zone[0][1] < y_center < zone[1][1]:
                # 判斷行人是否靠近機車
                for mx_min, my_min, mx_max, my_max in motorcycles:
                    if (x_min < mx_max and x_max > mx_min) and (y_min < my_max and y_max > my_min):
                        # 如果行人邊界框與機車邊界框重疊，則忽略該行人
                        return False
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

def process_frame(state, start_time, detection_start_time, pedestrian_in_zone, color_map):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 將畫面旋轉 15 度
        rotated_frame = rotate_frame(frame, 5)

        objects = detect_objects(rotated_frame, yolo_model, classes=[0, 2, 3])
        draw_bounding_boxes(rotated_frame, objects, color_map)

        # 從 Arduino 獲取距離
        sensor_state = get_state_from_sensor()
        if sensor_state is None:
            continue

        pedestrian_detected = check_pedestrian_in_zone(objects, WAITING_ZONE, sensor_state)
        prev_state = state
        state, detection_start_time, pedestrian_in_zone, start_time = traffic_light_control(
            state, pedestrian_detected, detection_start_time, pedestrian_in_zone, start_time
        )

        # 當燈號改變時，傳送狀態到 Arduino
        if state != prev_state:
            send_light_state_to_arduino(state)

        # 繪製等待區
        cv2.rectangle(rotated_frame, WAITING_ZONE[0], WAITING_ZONE[1], (0, 0, 255) if state == "RED" else (0, 255, 0), 2)

        # 顯示紅綠燈狀態
        time_left = int(DETECTION_TIME - (time.time() - detection_start_time)) if state == "RED" and detection_start_time else 0
        if state == "RED":
            cv2.putText(rotated_frame, f"Light: RED", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if detection_start_time:
                cv2.putText(rotated_frame, f"Switching in: {time_left}s", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        elif state == "GREEN":
            cv2.putText(rotated_frame, f"Light: GREEN", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if not pedestrian_detected:
                time_left = int(RED_LIGHT_TIME - (time.time() - start_time))
                cv2.putText(rotated_frame, f"Switching to RED in: {time_left}s", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 顯示畫面
        cv2.imshow("Pedestrian and Vehicle Detection", rotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    state = "RED"
    start_time = time.time()
    detection_start_time = None
    pedestrian_in_zone = False

    color_map = {
        0: (0, 255, 0),  # 行人：綠色
        2: (255, 0, 0),  # 汽車：藍色
        3: (0, 0, 255)   # 機車：紅色
    }

    process_frame(state, start_time, detection_start_time, pedestrian_in_zone, color_map)

if __name__ == "__main__":
    main()
