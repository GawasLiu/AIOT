# IOT路口辨識號誌燈
## 組員
劉日軒 陳冠學 邱立晟 游茜雯 林大鈞

## 專案描述
本專案旨在透過 IOT 技術實現路口號誌燈辨識系統，利用 Python 作為中間平台接收 Arduino 的感測資料與影像資訊，並根據分析結果控制號誌燈的狀態，以提升交通效率與安全性。

## 功能特色
- 接收並處理 Arduino 傳輸的感測數據。
- 整合影像辨識技術以檢測交通狀況。
- 動態控制號誌燈以適應不同交通情境。
- 支援實時數據傳輸與系統反應。
- 將燈號變換紀錄進資料，並顯示在網頁上。

## 使用技術
- **程式語言**: Python、C++ (Arduino)
- **硬體**: Arduino 開發、LED 號誌燈模組、HC-SR04超音波感測器
- **影像處理**: OpenCV
- **物件辨識**: Ultralytics YOLO
- **資料庫**: XAMPP(Mysql)
- **資料庫網頁互動**: Pymysql、Flask

## 安裝與使用方法

### 環境需求
1. Python 3.8 或更新版本
2. Arduino IDE
3. XAMPP

### 設備連接
將 Arduino 開發板與感測器/LED 號誌燈模組連接。
![SR-04](https://github.com/GawasLiu/AIOT/blob/main/SR-04.png)

### 執行步驟
1. 上傳 Arduino 程式碼至開發板。
2. 啟動 Python 腳本：
3. I.查看控制台輸出。
II.檢查號誌燈反應。
III.查看資料庫及網頁資料。

## 專案結構
```
├── app.py                        # 主程式入口
├── templates                     # 網頁模板目錄
├── Arduino/SR04                  # Arduino 程式碼目錄
├── SR-04.png                     # Arduino 接線圖
├── 裝置互動.png                   # 裝置互動圖
├── README.md                     # 專案說明文件
├── 專案簡報.ppt
```
