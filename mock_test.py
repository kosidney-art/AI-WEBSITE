import json
import http.server
import socketserver
import webbrowser
from PIL import Image, ImageDraw

# 1. 生成虛擬的新聞數據 data.json
mock_data = [
    {
        "title": "OpenAI 預計明早推出 GPT-5.5，推理能力提升 10 倍",
        "category": "技術突破",
        "summary": [
            "全新結構支援更強大的長鏈路自主推理，工程代碼能力碾壓前代。",
            "原生整合實時多模態語音與視覺，響應延遲縮短至人類水平。",
            "內建智慧溶斷機制，防止 Agent 在自動化任務中陷入死循環。"
        ]
    },
    {
        "title": "DeepSeek V4 開源模型震撼發佈，核心推理成本暴跌 90%",
        "category": "開源工具",
        "summary": [
            "極致的架構優化，使其性能在多項基準測試中直逼頂級閉源模型。",
            "全面支持 100 萬超長上下文窗口，適合大規模開源專案重構。",
            "提供標準 OpenAI API 接口，現有自動化流水線可一秒無痛遷移。"
        ]
    }
]

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(mock_data, f, ensure_ascii=False, indent=4)

# 2. 用 Pillow 測試繪製一張虛擬的 IG 圖片
img = Image.new('RGB', (1080, 1080), color=(15, 23, 42))
d = ImageDraw.Draw(img)
try:
    d.text((100, 100), "Global AI Daily Brief", fill=(255, 255, 255))
    d.text((100, 180), "Mock Test Image Success!", fill=(56, 189, 248))
    img.save('ig_today.png')
    print("✅ 成功模擬生成 data.json 與 ig_today.png 圖片！")
except Exception as e:
    print(f"❌ 圖片生成失敗: {e}")

# 3. 啟動本地 HTTP 伺服器並自動打開網頁
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

print(f"🚀 本地測試伺服器已啟動！連接埠: {PORT}")
print("👉 正在為您自動打開瀏覽器... 如果沒有彈出，請手動輸入: http://localhost:8000")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    webbrowser.open(f"http://localhost:8000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 伺服器已安全關閉。")
