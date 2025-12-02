import json
import streamlit as st
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. 雲端資料庫連線設定
# ==========================================

def get_db_connection():
    """連線到 Google Sheets (支援 本機 key.json 與 雲端 Secrets JSON字串 雙模式)"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    try:
        # 1. 優先嘗試：從 Streamlit 雲端 Secrets 讀取 (新寫法：讀取 JSON 字串)
        if "gcp_service_account" in st.secrets:
            # 這裡多了一個 json.loads 把文字轉回字典
            creds_dict = json.loads(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # 2. 備用方案：從本機 key.json 讀取
            creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
            
        client = gspread.authorize(creds)
        sh = client.open("bar_master_db")
        return sh
    except Exception as e:
        st.error(f"連線失敗！請檢查 Secrets 設定或 key.json。\n錯誤訊息: {e}")
        return None
# 初始化連線 (全域變數)
SH = get_db_connection()

# ==========================================
# 2. 資料讀寫輔助函數 (Helper Functions)
# ==========================================

def get_data(worksheet_name):
    """從指定分頁讀取所有資料 (回傳列表)"""
    if SH:
        try:
            worksheet = SH.worksheet(worksheet_name)
            return worksheet.get_all_records()
        except:
            st.warning(f"找不到分頁: {worksheet_name}")
            return []
    return []

def add_data(worksheet_name, row_data):
    """新增一筆資料到指定分頁"""
    if SH:
        worksheet = SH.worksheet(worksheet_name)
        worksheet.append_row(row_data)

def update_job_status(job_id, taker_name):
    """更新工作狀態 (專用於接案功能)"""
    if SH:
        worksheet = SH.worksheet('jobs')
        # 尋找那筆工作的列數 (比較複雜，因為要找 ID)
        cell = worksheet.find(str(job_id))
        if cell:
            # 更新 Status (第 6 欄) 和 Taker (第 7 欄)
            worksheet.update_cell(cell.row, 6, "Taken")
            worksheet.update_cell(cell.row, 7, taker_name)

# ==========================================
# 3. 功能模組 (配合雲端資料修改版)
# ==========================================

def page_login():
    st.title("🔐 Bar Master 雲端版")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    
    if st.button("登入"):
        # 這裡為了簡化，先保留寫死的帳號驗證
        # 你也可以在 Sheet 建立一個 users 分頁來管理
        valid_users = {"admin": "admin", "leo": "1234", "guest": "0000"}
        
        if username in valid_users and valid_users[username] == password:
            st.success("登入成功！")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

def page_recipes():
    st.header("📖 雲端酒譜資料庫")
    
    # 從 Google Sheet 讀取資料
    recipes_data = get_data('recipes') # 欄位: name, ingredients
    
    search = st.text_input("🔍 搜尋酒譜", placeholder="例如: Gin")
    
    for r in recipes_data:
        # 資料庫讀出來是 Dictionary: {'name': 'Gin Tonic', 'ingredients': 'Gin:45, Tonic:120'}
        name = r['name']
        ing_str = r['ingredients'] # 字串格式
        
        if search == "" or search.lower() in name.lower():
            with st.expander(f"🍸 {name}"):
                st.write("**所需材料：**")
                # 解析字串 "Gin:45, Tonic:120" 變成條列式
                try:
                    items = ing_str.split(',')
                    for item in items:
                        st.write(f"- {item.strip()}")
                except:
                    st.write(ing_str)

def page_ingredients():
    st.header("🍋 雲端庫存管理")
    
    # 讀取庫存
    inventory_data = get_data('inventory') # 欄位: item_name
    current_items = [row['item_name'] for row in inventory_data]
    
    col1, col2 = st.columns([3, 1])
    new_item = col1.text_input("新增材料", label_visibility="collapsed")
    
    if col2.button("➕ 加入"):
        if new_item and new_item not in current_items:
            # 寫入 Google Sheet
            add_data('inventory', [new_item])
            st.success(f"已上傳 {new_item}")
            time.sleep(1)
            st.rerun()

    st.subheader("目前庫存：")
    for item in current_items:
        st.text(f"📦 {item}")
    
    st.caption("提示：刪除功能建議直接去 Google Sheet 操作")

def page_job_center():
    st.header("💼 即時接案中心")
    
    # 從 Google Sheet 讀取最新工作
    jobs_data = get_data('jobs')
    
    tab1, tab2 = st.tabs(["🔥 接案大廳", "✅ 我的任務"])
    
    with tab1:
        # 篩選出 Open 的工作
        open_jobs = [j for j in jobs_data if j['status'] == "Open"]
        
        if not open_jobs:
            st.info("目前沒有新案件。")
            
        for job in open_jobs:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(job['title'])
                    st.write(f"📅 {job['date']} | 📍 {job['location']} | 💰 {job['budget']}")
                with c2:
                    st.write("")
                    if st.button("⚡ 接案", key=f"job_{job['id']}"):
                        # 更新 Google Sheet
                        update_job_status(job['id'], st.session_state["username"])
                        st.toast(f"已接下案件！")
                        time.sleep(1)
                        st.rerun()

    with tab2:
        # 篩選出 我接的 工作
        my_jobs = [j for j in jobs_data if j['taker'] == st.session_state["username"]]
        for job in my_jobs:
            with st.container(border=True):
                st.subheader(f"✅ {job['title']}")
                st.write(f"📅 {job['date']} | 📍 {job['location']}")
                st.success("狀態：已確認")

# (其他計算機功能保持不變，為了版面我不重複貼，請保留之前的計算機函數)
def page_abv_calculator():
    st.header("🧮 酒精濃度計算機")
    # ... (請保留之前的程式碼)
    st.info("功能維護中") 

def page_glassware():
    st.header("🥂 酒杯換算")
    # ... (請保留之前的程式碼)
    st.info("功能維護中")

def page_decanting():
    st.header("🍷 醒酒建議")
    # ... (請保留之前的程式碼)
    st.info("功能維護中")

def page_tutorials():
    st.header("📚 調酒師學院")
    st.info("教學資料庫串接中...")

def page_user_profile():
    st.header("👤 會員中心")
    st.write(f"ID: {st.session_state['username']}")
    if st.button("登出"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==========================================
# 4. 主程式控制
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    page_login()
else:
    with st.sidebar:
        st.title("🍹 Bar Master Cloud")
        st.write(f"Hi, {st.session_state['username']}")
        menu = {
            "📖 雲端酒譜": page_recipes,
            "🍋 庫存管理": page_ingredients,
            "💼 接案中心": page_job_center,
            "👤 會員中心": page_user_profile,
            # 其他功能先隱藏或自行加回
        }
        choice = st.radio("選單", list(menu.keys()))
    
    menu[choice]()