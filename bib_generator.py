# bib_generator.py
# 這是我們活動的核心：號碼布生成引擎

import os
from PIL import Image, ImageDraw, ImageFont  # 引入強大的修圖函式庫 Pillow

def create_bib(user_name, user_declaration, bib_number, photo_path):
    print(f"🔄 開始製作 {user_name} 的號碼布...")

    # --- 1. 設定檔案路徑 ---
    base_dir = "assets"
    template_path = os.path.join(base_dir, "template.jpg")
    font_path = os.path.join(base_dir, "font.ttf")
    
    # --- 2. 載入底圖 ---
    # Convert("RGBA") 是為了確保支援透明度處理
    bib_image = Image.open(template_path).convert("RGBA")
    width, height = bib_image.size
    print(f"✅ 底圖載入成功，尺寸: {width}x{height}")

    # --- 3. 處理用戶照片 (模擬 A 組拼圖或是照片貼上的效果) ---
    try:
        user_photo = Image.open(photo_path).convert("RGBA")
        
        # 重新調整照片大小 (這裡設定為寬度的 30%)
        photo_w = int(width * 0.3)
        # 等比例縮放
        ratio = photo_w / user_photo.width
        photo_h = int(user_photo.height * ratio)
        user_photo = user_photo.resize((photo_w, photo_h))
        
        # 貼上照片 (假設貼在左側中間位置，你可以修改座標)
        # (50, 200) 是座標 x, y
        bib_image.paste(user_photo, (50, 250), user_photo) 
        print("✅ 用戶照片合成完畢")
    except Exception as e:
        print(f"⚠️ 找不到照片或照片錯誤: {e}")

    # --- 4. 準備畫筆 ---
    draw = ImageDraw.Draw(bib_image)

    # --- 5. 寫上流水號 (2026-00088) ---
    # 設定字體大小 (根據底圖大小動態調整，這裡設為高度的 15%)
    num_font_size = int(height * 0.15)
    try:
        num_font = ImageFont.truetype(font_path, num_font_size)
    except:
        num_font = ImageFont.load_default() # 如果找不到字型就用預設
        print("⚠️ 找不到指定字型，使用預設字型")

    bib_str = f"NO.{bib_number:05d}" # 補零格式，例如 00088
    
    # 算出文字寬度，為了要置中
    # textbbox 是 Pillow 新版取得文字大小的方法
    left, top, right, bottom = draw.textbbox((0, 0), bib_str, font=num_font)
    text_w = right - left
    text_h = bottom - top
    
    # 畫在正中間 (x = 畫布一半 - 文字一半)
    x = (width - text_w) / 2
    y = (height - text_h) / 2
    
    # 壓上黑色文字
    draw.text((x, y), bib_str, font=num_font, fill="black")
    print(f"✅ 流水號 {bib_str} 寫入完畢")

    # --- 6. 寫上宣言 (給未來的自己) ---
    dec_font_size = int(height * 0.05) # 字體小一點
    try:
        dec_font = ImageFont.truetype(font_path, dec_font_size)
    except:
        dec_font = ImageFont.load_default()

    declaration = f"{user_name}: {user_declaration}"
    
    # 再次計算寬度以置中
    left, top, right, bottom = draw.textbbox((0, 0), declaration, font=dec_font)
    dec_w = right - left
    
    # 畫在底部
    dec_x = (width - dec_w) / 2
    dec_y = height - (height * 0.15) # 底部留 15% 空間
    
    draw.text((dec_x, dec_y), declaration, font=dec_font, fill="darkblue")
    print(f"✅ 宣言 '{declaration}' 寫入完畢")

    # --- 7. 存檔 ---
    output_filename = f"output_{bib_number:05d}.jpg"
    # 轉回 RGB 才能存成 JPG
    bib_image.convert("RGB").save(output_filename, quality=95)
    
    print(f"🎉 成功！檔案已儲存為: {output_filename}")
    # 在 Windows 自動打開圖片給你看
    try:
        os.startfile(output_filename)
    except:
        pass

# --- 程式進入點 ---
if __name__ == "__main__":
    # 模擬資料：假設這是從 LINE 傳來的資料
    fake_user_name = "熱血阿豪"
    fake_declaration = "2026 我要破 PB！"
    fake_bib_number = 88
    fake_photo_path = "assets/photo.jpg"

    # 執行合成
    create_bib(fake_user_name, fake_declaration, fake_bib_number, fake_photo_path)