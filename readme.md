# 🧊 冰箱 AI 料理助手

使用 AI 讓你的冰箱變身智慧廚神！  
只需上傳冰箱照片，系統即自動辨識食材並推薦可做的料理，還提供語音導煮功能。

---

## 🚀 功能特色

- 📸 上傳冰箱或食材照片，自動辨識可用食材
- 🧠 使用 GPT 推薦適合的食譜（含分類、風味標籤）
- 📋 查看推薦食譜與缺料提示
- 📄 查看每道料理的詳細做法
- 🔊 語音導煮，每個步驟皆可播放語音說明
- 💾 所有推薦都快取儲存於本地資料庫，避免重複呼叫

---

## 📁 專案結構

ai-fridge-gpt/
├── app.py # Streamlit 主應用程式
├── requirements.txt # 套件依賴清單
├── README.md # 本說明文件
├── data/ # SQLite 資料庫與快取資料夾
│ └── db.sqlite3
├── recipe_images/ # 食譜圖片（可選）
├── audio_cache/ # 語音快取資料夾（gTTS 生成）
├── uploads/ # 上傳的食材照片
├── src/
│ ├── db_utils.py # 資料庫處理邏輯
│ ├── prompt_templates.py # 所有 GPT 提示詞
│ ├── gpt_utils.py # GPT 處理與快取邏輯
│ └── ui_utils.py # 所有 UI 畫面與互動邏輯



## 🛠️ 安裝與執行

### 1️⃣ 安裝必要套件

請使用 Python 3.10+，並在虛擬環境中執行：

```bash
pip install -r requirements.txt
2️⃣ 執行應用程式

streamlit run app.py
🧪 測試範例
你可以將一張食材照片放入 /uploads 資料夾中或從 UI 上傳。

uploads/
└── e6df36bd51a20d2391a5f758e4ee5950.jpg
上傳後會自動觸發以下流程：

使用 GPT Vision 分析圖片食材

呼叫 GPT 推薦 3-5 道可做的料理

顯示食譜與缺料、分類、風味等資訊

點選任一食譜可進入詳情，逐步查看步驟與語音導煮

