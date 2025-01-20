# IOT路口辨識號誌燈

## 專案描述
本專案旨在透過 IOT 技術實現路口號誌燈辨識系統，利用 Python 作為中間平台接收 Arduino 的感測資料與影像資訊，並根據分析結果控制號誌燈的狀態，以提升交通效率與安全性。

## 功能特色
- 接收並處理 Arduino 傳輸的感測數據。
- 整合影像辨識技術以檢測交通狀況。
- 動態控制號誌燈以適應不同交通情境。
- 支援實時數據傳輸與系統反應。

## 使用技術
- **程式語言**: Python、C++ (Arduino)
- **硬體**: Arduino 開發板、攝影機模組、LED 號誌燈模組
- **通訊技術**: UART、I2C
- **影像處理**: OpenCV
- **物件辨識**: Ultralytics YOLO

## 安裝與使用方法

### 環境需求
1. Python 3.8 或更新版本
2. Arduino IDE
3. 安裝以下 Python 套件：
    ```bash
    pip install opencv-python pyserial ultralytics
    ```

### 設備連接
1. 將 Arduino 開發板與感測器/LED 號誌燈模組連接。
2. 將攝影機模組連接至主控電腦。

### 執行步驟
1. 上傳 Arduino 程式碼至開發板。
2. 啟動 Python 腳本：
    ```bash
    python main.py
    ```
3. 查看控制台輸出或檢查號誌燈反應。

## 專案結構
```
├── program/main.py               # 主程式入口
├── arduino_code/                 # Arduino 程式碼目錄
├── README.md                     # 專案說明文件
├── 裝置互動.dwario                # 裝置互動圖
```