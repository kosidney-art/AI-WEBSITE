name: 24H 雲端 AI 高層自動聯網作戰流程

on:
  # 1. 允許老細隨時手動一鍵開機
  workflow_dispatch:
  
  # 2. 定時自動開機（每 6 小時全自動執行一次）
  schedule:
    - cron: '0 */6 * * *'

jobs:
  run-corporate-brain:
    runs-on: ubuntu-latest

    steps:
    # 🏎️ 步驟一：拉取老細最新嘅代碼
    - name: Checkout Repository
      uses: actions/checkout@v4

    # 🐍 步驟二：喺雲端架設正確嘅 Python 環境（已全面修正為 setup-python@v5）
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    # 📦 步驟三：自動安裝所有網絡傳輸晶片與免費搜尋套件
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests duckduckgo_search

    # 🧠 步驟四：正式開機！執行 office_agent.py 進行聯網撈料、高層吵架
    - name: Run AI C-Suite Agent
      env:
        LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
        TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
      run: |
        python office_agent.py

    # 💾 步驟五：將高層會議完工、撈到嘅最新 JSON 資料自動儲存並推送到網頁更新
    - name: Commit and Push Updated Data
      run: |
        git config --global user.name "GitHub Action Bot"
        git config --global user.email "actions@github.com"
        git add office_log.json data.json tasks.json || true
        git commit -m "🤖 報告老細：雲端 AI 高層已完成最新聯網搜尋與資料更新" || true
        git push
