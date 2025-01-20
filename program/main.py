import cv2
import time
import mediapipe as mp
import serial

# 初始化串口
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(1)

# 初始化 MediaPipe 模組
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 等待區的區域座標（畫面中設定的矩形區域）
WAITING_ZONE = [(10, 10), (630, 470)]

# 初始化攝影機
cap = cv2.VideoCapture(0)

# 紅綠燈狀態模擬
RED_LIGHT_TIME = 10  # 紅燈時間（秒）
DETECTION_TIME = 2   # 行人進入等待區後轉綠燈的時間（秒）
state = "RED"        # 初始狀態為紅燈
start_time = time.time()
detection_start_time = None  # 用來記錄行人進入等待區的時間
pedestrian_in_zone = False   # 用來記錄行人是否在等待區內

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 偵測行人
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # 判斷行人是否進入等待區
    pedestrian_detected = False
    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
            if WAITING_ZONE[0][0] < x < WAITING_ZONE[1][0] and WAITING_ZONE[0][1] < y < WAITING_ZONE[1][1]:
                pedestrian_detected = True
                break

    # 狀態切換邏輯
    if state == "RED":
        if pedestrian_detected:
            if detection_start_time is None:
                detection_start_time = time.time()  # 開始記錄行人進入時間
            elif time.time() - detection_start_time >= DETECTION_TIME:
                state = "GREEN"  # 行人進入超過2秒，轉為綠燈
                pedestrian_in_zone = True
                detection_start_time = None
        else:
            detection_start_time = None  # 行人未持續進入，重置計時器
    elif state == "GREEN":
        if not pedestrian_detected:
            if pedestrian_in_zone:
                start_time = time.time()  # 行人離開區域，開始倒數10秒
                pedestrian_in_zone = False
        else:
            start_time = time.time()  # 行人再次進入等待區，重置倒數計時器
            pedestrian_in_zone = True

        if time.time() - start_time >= RED_LIGHT_TIME and not pedestrian_detected:
            state = "RED"  # 綠燈倒數結束，且區域內無行人，轉為紅燈

    # 繪製等待區
    cv2.rectangle(frame, WAITING_ZONE[0], WAITING_ZONE[1], (0, 0, 255) if state == "RED" else (0, 255, 0), 2)

    # 顯示行人狀態
    if pedestrian_detected:
        cv2.putText(frame, "Pedestrian in zone!", (15, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 顯示紅綠燈狀態與倒數計時
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

    # 顯示人體骨架
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # 顯示畫面
    cv2.imshow("Pedestrian Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()