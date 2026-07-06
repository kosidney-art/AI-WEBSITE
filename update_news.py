import os
import json
import feedparser
import requests
import smtplib
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# ==================== 1. 核心環境變數配置 ====================
API_TYPE = os.getenv('API_TYPE', 'anthropic') # 'anthropic' 或 'openai_compatible'
BASE_URL = os.getenv('BASE_URL', 'https://api.anthropic.com/v1/messages')
API_KEY = os.getenv('LLM_API_KEY', '')
MODEL_NAME = os.getenv('MODEL_NAME', 'claude-3-5-sonnet-20241022')

# Instagram & Email 配置
IG_USER_ID = os.getenv('IG_USER_ID', '')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', '')

# ==================== 2. 萬能 LLM 適配器 ====================
def call_llm(prompt):
    if not API_KEY:
        print("⚠️ 未偵測到 LLM_API_KEY，跳過 AI 處理。")
        return None
    
    headers = {"Content-Type": "application/json"}
    
    if API_TYPE == 'anthropic':
        headers["x-api-key"] = API_KEY
        headers["anthropic-version"] = "2023-06-01"
        data = {
            "model": MODEL_NAME,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
    else: # OpenAI 兼容模式 (例如 DeepSeek)
        headers["Authorization"] = f"Base {API_KEY}" if "deepseek" in BASE_URL else f"Bearer {API_KEY}"
        data = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=30)
        res_json = response.json()
        if API_TYPE == 'anthropic':
            return res_json['content'][0]['text']
        else:
            return res_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ LLM 調用失敗: {e}")
        return None

# ==================== 3. 核心業務邏輯流水線 ====================
def main():
    print("🌐 正在抓取全球 AI 新聞...")
    feed = feedparser.parse("https://news.google.com/rss/search?q=Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en")
    
    articles = feed.entries[:15] # 抓取前15條進行篩選
    if not articles:
        print("❌ 未能抓取到任何新聞，系統安全退出。")
        return

    # 打包新聞給 AI 進行智能去重與精選
    raw_text = "\n".join([f"Title: {a.title}\nLink: {a.link}\n---" for a in articles])
    
    prompt = f"""
    你是一個高級 AI 新聞主編。請從以下原始新聞中，剔除重複事件、無聊八卦，篩選出今天最重要的 3 條科技突破、融資或開源神兵事件。
    請嚴格遵守以下 JSON 格式輸出，不要包含任何額外解釋文字或 markdown 標記：
    [
      {{
        "title": "繁體中文精簡新聞標題",
        "category": "技術突破/商業融資/開源工具",
        "summary": ["廣東話/繁體中文精闢要點1", "廣東話/繁體中文精闢要點2", "廣東話/繁體中文精闢要點3"],
        "url": "原始連結"
      }}
    ]
    
    原始新聞內容：
    {raw_text}
    """
    
    print("🤖 正在調用 AI 進行智能聚合與翻譯...")
    llm_output = call_llm(prompt)
    if not llm_output:
        return
        
    try:
        # 清洗可能帶有 markdown 的不乾淨 JSON
        clean_json = llm_output.strip().replace("```json", "").replace("```", "")
        today_news = json.loads(clean_json)
    except Exception as e:
        print(f"❌ JSON 解析失敗，AI 輸出格式不正確: {e}\n{llm_output}")
        return

    # 數據持久化與30天歷史裁剪
    data_file = 'data.json'
    history_data = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except: pass
        
    # 將新數據插入頂部，並裁剪最多保留50條
    updated_history = (today_news + history_data)[:50]
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(updated_history, f, ensure_ascii=False, indent=4)
    print("💾 data.json 數據庫更新成功！")

    # ==================== 4. 自動畫 IG 懶人包字卡 ====================
    print("🎨 正在自動繪製 Instagram 科技感字卡...")
    img = Image.new('RGB', (1080, 1080), color=(15, 23, 42)) # 深色底
    d = ImageDraw.Draw(img)
    # Actions 部署時會自動安裝中文字體，Linux 預設路徑如下
    font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    if not os.path.exists(font_path): font_path = "Arial" # 本地降級備用
    
    try:
        # 簡單畫一些發光霓虹線條與文字排版
        d.rectangle([(40, 40), (1040, 1040)], outline=(56, 189, 248), width=3)
        d.text((80, 80), f"AI DAILY BRIEF - {datetime.now().strftime('%Y/%m/%d')}", fill=(255, 255, 255))
        
        y_offset = 200
        for item in today_news[:3]:
            d.text((80, y_offset), f"[{item['category']}] {item['title']}", fill=(56, 189, 248))
            y_offset += 60
            for s in item['summary']:
                d.text((120, y_offset), f"• {s[:35]}...", fill=(203, 213, 225))
                y_offset += 45
            y_offset += 40
            
        img.save('ig_today.png')
        print("🖼️ IG 字卡 ig_today.png 繪製成功！")
    except Exception as e:
        print(f"⚠️ 畫圖失敗: {e}")

    # ==================== 5. 生成 Threads 爆款文案並發送 Email ====================
    if today_news and SENDER_EMAIL and SMTP_PASSWORD:
        print("✍️ 正在生成 Threads 爆款文案並寄送電郵...")
        threads_prompt = f"請將以下這條今日最勁嘅 AI 新聞，改寫成一條適合發布在 Threads 平台嘅爆款短文（廣東話風格）。要求：極具觀點、有 Hook、多用 Emoji、排版多留白方便手機閱讀：\n{json.dumps(today_news[0], ensure_ascii=False)}"
        threads_post = call_llm(threads_prompt)
        
        if threads_post:
            msg = MIMEText(f"<h3>老闆！今日份專屬 Threads 爆款文案已送達：</h3><pre style='white-space:pre-wrap; font-family:sans-serif; font-size:16px;'>{threads_post}</pre>", 'html', 'utf-8')
            msg['Subject'] = f"🚀 今日 AI 爆料與 Threads 文案直送 ({datetime.now().strftime('%m/%d')})"
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            
            try:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SENDER_EMAIL, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
                server.quit()
                print("📧 Threads 文案已成功射入你個 Email 信箱！")
            except Exception as e:
                print(f"⚠️ 電郵發送失敗: {e}")

if __name__ == '__main__':
    main()
