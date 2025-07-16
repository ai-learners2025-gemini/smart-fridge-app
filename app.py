import os
import sqlite3
import json
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai # NEW: 匯入 Google 的 Generative AI 
import traceback

# --- App 設定 ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-very-secret-key-for-gemini' # 建議更換

# --- Gemini API 設定 ---
# 從 Google AI Studio 取得您的 API 金鑰 (https://aistudio.google.com/)
# 建議使用環境變數來保護金鑰。
# 在終端機設定:
# Windows: set GOOGLE_API_KEY=你的金鑰
# macOS/Linux: export GOOGLE_API_KEY=你的金鑰
try:
    # NEW: 設定 Gemini API 金鑰
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("錯誤：請先設定您的 GOOGLE_API_KEY 環境變數。")
    # 為了方便展示，如果沒有環境變數，請將您的金鑰直接貼在下方
    # 但強烈建議不要這樣做在正式專案中！
    # genai.configure(api_key="YOUR_GOOGLE_AI_API_KEY")


# --- 資料庫設定 (維持不變) ---
DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# schema.sql 檔案維持不變，此處省略

# --- API 端點 (Endpoints) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/identify-ingredients', methods=['POST'])
def identify_ingredients():
    # 此模擬端點維持不變
    identified_items = ['雞蛋', '玉米', '鮮奶']
    return jsonify({
        "success": True,
        "ingredients": identified_items
    })


@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe_api():
    """
    接收食材，呼叫 Gemini API 生成食譜，存入資料庫並回傳。
    """
    data = request.get_json()
    ingredients = data.get('ingredients')
    
    if not ingredients:
        return jsonify({"success": False, "error": "缺少食材"}), 400

    try:
        # --- NEW: 呼叫 Gemini 1.5 Flash API ---

        # 1. 設定模型，並指定回傳格式為 JSON
        generation_config = {
            "response_mime_type": "application/json",
        }
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config=generation_config
        )

        # 2. 建立 Prompt (與之前相同，Gemini 完全相容)
        prompt = f"""
        你是一位專業的台灣料理主廚。請使用以下食材：{', '.join(ingredients)}，
        設計一道美味、簡單、適合家庭的料理。

        請嚴格按照以下 JSON 格式回傳，不要有任何多餘的文字或解釋：
        {{
          "title": "食譜的創意名稱",
          "description": "一句話的吸引人描述",
          "prep_time": "準備時間 (例如: 5 分鐘)",
          "cook_time": "烹飪時間 (例如: 10 分鐘)",
          "servings": "份量 (例如: 2人份)",
          "ingredients": [
            {{ "name": "食材名稱", "quantity": "數量與單位" }},
            {{ "name": "...", "quantity": "..." }}
          ],
          "seasonings": [
            {{ "name": "調味料名稱", "quantity": "數量與單位" }},
            {{ "name": "...", "quantity": "..." }}
          ],
          "steps": [
            "詳細步驟一",
            "詳細步驟二",
            "..."
          ],
          "chef_tip": "一個專業的主廚小提示"
        }}
        """

        # 3. 產生內容
        response = model.generate_content(prompt)

        # 4. 解析回傳的 JSON 文字
        recipe_data = json.loads(response.text)

        # --- 將食譜存入資料庫 (維持不變) ---
        db = get_db()
        db.execute(
            'INSERT INTO recipes (title, ingredients, steps) VALUES (?, ?, ?)',
            (recipe_data['title'], json.dumps(recipe_data, ensure_ascii=False), json.dumps(recipe_data['steps'], ensure_ascii=False))
        )
        db.commit()
        db.close()

        return jsonify({"success": True, "recipe": recipe_data})

    except Exception as e:
        print(f"發生錯誤: {e}")
        return jsonify({"success": False, "error": "AI 生成食譜失敗，請稍後再試。"}), 500


# --- 【修改這裡】增強版的錯誤捕捉 ---
    except Exception as e:
        print("\n" + "="*50)
        print("====== AI API 呼叫時發生嚴重錯誤 ======")
        print(f"====== 錯誤類型: {type(e).__name__}")
        print(f"====== 錯誤訊息: {e}")
        print("====== 詳細追蹤日誌 (Traceback):")
        traceback.print_exc() # 這會印出最詳細的錯誤堆疊資訊
        print("="*50 + "\n")
        
        # 回傳給前端的訊息也可以更具體一點
        error_message_for_frontend = f"AI生成食譜失敗，請查看後端終端機的詳細錯誤日誌。錯誤類型: {type(e).__name__}"
        return jsonify({"success": False, "error": error_message_for_frontend}), 500

if __name__ == '__main__':
    # 【重要】取消註解下面這幾行，來初始化資料庫
    # 這個動作只需要在第一次執行時做一次
    with app.app_context():
        db = get_db()
        # 確認 schema.sql 檔案存在於同一個 backend 資料夾
        try:
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())
            print("✅ 資料庫初始化成功！ 'recipes' 資料表已建立。")
        except FileNotFoundError:
            print("❌ 錯誤：找不到 schema.sql 檔案，請確認它與 app.py 在同一個資料夾中。")
        db.close()
    
    app.run(debug=True, port=5000)