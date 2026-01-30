# app.py - 2026 全城尋寶戰核心引擎 (含獎品管理功能)
from flask import Flask, request, jsonify, send_from_directory
import os
import time
import json
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, static_folder='static')

OUTPUT_FOLDER = os.path.join('static', 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
COUNTER_FILE = "counter.txt"

def get_next_bib_number():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f: f.write("0")
    with open(COUNTER_FILE, "r") as f:
        try: current = int(f.read().strip())
        except: current = 0
    next_count = current + 1
    with open(COUNTER_FILE, "w") as f: f.write(str(next_count))
    return next_count

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

# --- 後台管理頁面 (顯示獎品) ---
@app.route('/admin')
def admin_panel():
    try:
        # 抓取所有圖片
        files = sorted(
            [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.jpg')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_FOLDER, x)),
            reverse=True
        )
    except: files = []
    
    html = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="10">
        <title>🖨️ 完賽號碼布列印後台</title>
        <style>
            body{font-family:'Microsoft JhengHei', sans-serif; padding:20px; background:#f0f0f0;}
            h2{color:#333; border-bottom:2px solid #00ffcc; padding-bottom:10px;}
            .grid{display:flex; flex-wrap:wrap; gap:20px;}
            .card{background:white; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); width:220px; text-align:center;}
            img{width:100%; height:auto; border:1px solid #ddd; margin-bottom:10px;}
            .btn{display:block; background:#007bff; color:white; padding:10px; text-decoration:none; border-radius:5px; font-weight:bold;}
            .btn:hover{background:#0056b3;}
            .time{font-size:0.8rem; color:#888; margin-bottom:5px;}
            .prize-box{background:#fff3cd; color:#856404; padding:8px; border-radius:5px; font-size:0.9rem; margin-bottom:10px; text-align:left;}
            .prize-title{font-weight:bold; font-size:0.8rem; display:block; margin-bottom:3px;}
        </style>
    </head>
    <body>
        <h2>🖨️ 即時接收總覽 (每10秒自動刷新)</h2>
        <div class="grid">
    """
    
    for f in files:
        t = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(os.path.join(OUTPUT_FOLDER, f))))
        
        # 嘗試讀取對應的獎品文字檔
        txt_filename = f.replace('.jpg', '.txt')
        txt_path = os.path.join(OUTPUT_FOLDER, txt_filename)
        prizes_html = "無獎品紀錄"
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as tf:
                try:
                    prizes = json.loads(tf.read())
                    # 將獎品陣列轉成列表
                    if prizes:
                        prizes_html = "<ul style='margin:0; padding-left:20px;'>" + "".join([f"<li>{p}</li>" for p in prizes]) + "</ul>"
                    else:
                        prizes_html = "未獲取獎品"
                except:
                    prizes_html = "資料格式錯誤"

        html += f"""
        <div class="card">
            <div class="time">接收時間: {t}</div>
            <img src="/static/output/{f}">
            <div class="prize-box">
                <span class="prize-title">🎁 應發放獎品：</span>
                {prizes_html}
            </div>
            <div style="margin-bottom:5px;word-break:break-all;font-size:12px">{f}</div>
            <a href="/static/output/{f}" target="_blank" class="btn">下載列印</a>
        </div>
        """
    html += "</div></body></html>"
    return html

@app.route('/generate', methods=['POST'])
def generate():
    user_text = request.form.get('text', 'Run For Future')
    user_id = request.form.get('userId', 'UNKNOWN')
    theme = request.form.get('theme', 'puzzle')
    # 接收獎品清單字串 (JSON 格式)
    prizes_json = request.form.get('prizes', '[]')
    
    uploaded_file = request.files.get('photo')

    print(f"📥 收到請求 | ID:{user_id} | 宣言:{user_text} | 獎品:{prizes_json}")

    try:
        # 1. 選擇底圖
        template_map = {
            'glitch': 'static/template_glitch.jpg',
            'puzzle': 'static/template_puzzle.jpg',
            'mosaic': 'static/template_mosaic.jpg'
        }
        template_path = template_map.get(theme, 'static/template.jpg')
        if not os.path.exists(template_path): template_path = 'static/template.jpg'

        base_img = Image.open(template_path).convert("RGB")
        base_w, base_h = base_img.size

        # 2. 合成照片
        if uploaded_file:
            user_img = Image.open(uploaded_file).convert("RGBA")
            target_w = int(base_w * 0.5)
            ratio = user_img.height / user_img.width
            target_h = int(target_w * ratio)
            max_h = int(base_h * 0.4)
            if target_h > max_h:
                target_h = max_h
                target_w = int(target_h / ratio)
            user_img = user_img.resize((target_w, target_h))
            paste_x = (base_w - target_w) // 2
            paste_y = int(base_h * 0.45)
            base_img.paste(user_img, (paste_x, paste_y), user_img)

        # 3. 繪製文字
        draw = ImageDraw.Draw(base_img)
        font_path = "static/font.ttf"
        font_size_num = int(base_h * 0.13)
        font_size_text = int(base_h * 0.05)
        
        try:
            font_num = ImageFont.truetype(font_path, font_size_num)
            font_text = ImageFont.truetype(font_path, font_size_text)
        except:
            font_num = ImageFont.load_default()
            font_text = ImageFont.load_default()

        seq_num = get_next_bib_number()
        bib_str = str(seq_num).zfill(5)
        
        # 繪製編號
        text_content = f"NO.{bib_str}"
        bbox = draw.textbbox((0, 0), text_content, font=font_num)
        w = bbox[2] - bbox[0]
        text_x = (base_w - w) / 2
        text_y = base_h * 0.22 
        stroke_width = int(base_h * 0.005)
        draw.text((text_x, text_y), text_content, fill=(255, 0, 60), font=font_num, stroke_width=stroke_width, stroke_fill="white")

        # 繪製宣言
        bbox2 = draw.textbbox((0, 0), user_text, font=font_text)
        w2 = bbox2[2] - bbox2[0]
        draw.text(((base_w - w2)/2, base_h * 0.88), user_text, fill=(20, 20, 20), font=font_text)

        # 4. 存檔 (圖片)
        out_name = f"{bib_str}_{theme}.jpg"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        base_img.save(out_path, quality=95)
        
        # 5. 存檔 (獎品資訊 - 存成同名的 txt 檔)
        txt_name = f"{bib_str}_{theme}.txt"
        txt_path = os.path.join(OUTPUT_FOLDER, txt_name)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(prizes_json)

        return jsonify({
            "status": "success",
            "imageUrl": f"/static/output/{out_name}",
            "bibNumber": bib_str
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🚀 尋寶戰後端引擎啟動中...")
    app.run(debug=True, host='0.0.0.0', port=5000)