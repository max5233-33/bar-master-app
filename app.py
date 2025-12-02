import streamlit as st
import time

# ==========================================
# 1. 模擬資料庫區 (Database Mockup)
# ==========================================

# A. 會員資料
USERS_DB = {
    "admin": "admin123",
    "guest": "1234",
    "leo": "8888"
}

# B. 酒譜資料
RECIPES_DB = {
    "Gin Tonic": {"Gin": 45, "Tonic Water": 120},
    "Martini": {"Gin": 60, "Dry Vermouth": 10},
    "Mojito": {"Rum": 45, "Sugar": 10, "Lime": 20, "Mint": "Handful", "Soda": 100},
    "Old Fashioned": {"Whiskey": 60, "Sugar Cube": 1, "Bitters": 2}
}

# C. 教學資料庫 (新功能)
TUTORIALS_DB = [
    {"category": "技術", "title": "搖盪法 (Shake) 核心技巧", "desc": "學習如何運用 Three-piece Shaker 打出完美綿密泡沫。", "link": "https://www.youtube.com/results?search_query=cocktail+shake+technique"},
    {"category": "技術", "title": "刻冰球 (Ice Carving) 入門", "desc": "一把冰刀，將方冰修成完美圓球的職人技藝。", "link": "https://www.youtube.com/results?search_query=ice+carving+bartender"},
    {"category": "知識", "title": "六大基酒歷史起源", "desc": "從藥酒到現代烈酒的演變史。", "link": "https://zh.wikipedia.org/wiki/基酒"},
    {"category": "管理", "title": "如何計算酒吧成本率 (Cost %)", "desc": "開店必備！精準控制你的利潤空間。", "link": "#"}
]

# D. 接案中心資料 (初始化放到 Session State，因為狀態會變)
if "jobs_db" not in st.session_state:
    st.session_state.jobs_db = [
        {"id": 101, "title": "私人遊艇派對調酒師", "date": "2024-12-25", "location": "淡水漁人碼頭", "budget": "$8,000", "status": "Open", "taker": None},
        {"id": 102, "title": "品牌新品發表會", "date": "2024-01-10", "location": "台北信義區", "budget": "$5,000", "status": "Open", "taker": None},
        {"id": 103, "title": "婚禮迎賓飲料區", "date": "2024-02-14", "location": "台中林酒店", "budget": "$12,000", "status": "Open", "taker": None},
    ]

# ==========================================
# 2. 功能模組函數
# ==========================================

def page_login():
    """登入頁面"""
    st.title("🔐 Bar Master 登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    
    if st.button("登入"):
        if username in USERS_DB and USERS_DB[username] == password:
            st.success("登入成功！")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")

def page_recipes():
    """1. 酒譜大全"""
    st.header("📖 經典酒譜資料庫")
    search = st.text_input("🔍 搜尋酒譜", placeholder="例如: Gin")
    for name, ingredients in RECIPES_DB.items():
        if search == "" or search.lower() in name.lower():
            with st.expander(f"🍸 {name}"):
                st.write("**所需材料：**")
                for item, amount in ingredients.items():
                    st.write(f"- {item}: {amount}")

def page_ingredients():
    """2. 材料管理"""
    st.header("🍋 冰箱材料管理")
    if "inventory" not in st.session_state:
        st.session_state.inventory = ["琴酒", "通寧水", "檸檬"]
        
    col1, col2 = st.columns([3, 1])
    new_item = col1.text_input("新增材料", label_visibility="collapsed", placeholder="輸入材料名稱...")
    if col2.button("➕ 加入"):
        if new_item and new_item not in st.session_state.inventory:
            st.session_state.inventory.append(new_item)
            st.success(f"已加入 {new_item}")
            time.sleep(0.5)
            st.rerun()

    st.subheader("庫存清單：")
    for item in st.session_state.inventory:
        c1, c2 = st.columns([4, 1])
        c1.text(f"📦 {item}")
        if c2.button("刪除", key=f"del_{item}"):
            st.session_state.inventory.remove(item)
            st.rerun()

def page_abv_calculator():
    """3. 濃度計算"""
    st.header("🧮 酒精濃度計算機")
    c1, c2 = st.columns(2)
    vol = c1.number_input("總液體量 (ml)", value=0.0, step=10.0)
    alc_vol = c2.number_input("純酒精總量 (ml)", value=0.0, step=5.0)
    st.caption("提示：純酒精總量 = 各材料容量 x (酒精度/100) 的總和")
    
    if vol > 0:
        abv = (alc_vol / vol) * 100
        st.metric("最終濃度 (ABV)", f"{abv:.2f}%")
        if abv > 30:
            st.warning("🔥 這杯很烈喔！")
        elif abv < 10:
            st.info("🍹 輕鬆易飲的濃度")

def page_glassware():
    """4. 酒杯換算"""
    st.header("🥂 酒杯換算小幫手")
    tab1, tab2 = st.tabs(["單位換算", "酒譜縮放"])
    
    with tab1:
        c1, c2 = st.columns(2)
        oz = c1.number_input("盎司 (oz)", min_value=0.0)
        c1.info(f"= {oz * 29.57:.1f} ml")
        ml = c2.number_input("毫升 (ml)", min_value=0.0)
        c2.info(f"= {ml / 29.57:.2f} oz")
        
    with tab2:
        st.write("想把 300ml 的酒譜改成 100ml 的杯子裝嗎？")
        orig = st.number_input("原酒譜總量", value=100.0)
        target = st.number_input("目標酒杯容量", value=60.0)
        if orig > 0:
            ratio = target / orig
            st.success(f"👉 所有材料請乘以 **{ratio:.2f}** 倍")

def page_decanting():
    """5. 醒酒建議"""
    st.header("🍷 醒酒建議")
    wine = st.selectbox("紅酒類型", ["波爾多 (Bordeaux)", "勃根地 (Burgundy)", "卡本內 (Cabernet)", "年輕紅酒", "老酒 (>15年)"])
    if st.button("分析建議"):
        advice = {
            "老酒 (>15年)": "⚠️ 不需醒酒，除去沉澱物即可，避免香氣散失。",
            "波爾多 (Bordeaux)": "🕒 建議 1 ~ 2 小時 (單寧強勁，需時間軟化)",
            "卡本內 (Cabernet)": "🕒 建議 1 ~ 2 小時 (酒體厚重)",
            "年輕紅酒": "🕒 建議 30 分鐘 ~ 1 小時 (讓封閉香氣打開)",
            "勃根地 (Burgundy)": "🕒 建議 0 ~ 30 分鐘 (風格優雅，不用太久)"
        }
        st.info(advice.get(wine, "適度醒酒即可"))

def page_tutorials():
    """7. 教學資料庫 (新功能)"""
    st.header("📚 調酒師學院")
    
    # 篩選器
    filter_cat = st.selectbox("選擇分類", ["全部", "技術", "知識", "管理"])
    
    for tutorial in TUTORIALS_DB:
        if filter_cat == "全部" or filter_cat == tutorial["category"]:
            with st.container():
                st.subheader(f"[{tutorial['category']}] {tutorial['title']}")
                st.write(tutorial['desc'])
                st.markdown(f"[👉 點擊觀看教學/相關文章]({tutorial['link']})")
                st.divider()

def page_job_center():
    """8. 接案中心 (新功能 - 核心邏輯)"""
    st.header("💼 接案中心")
    
    # 使用 Tab 分流：接案大廳 vs 我的任務
    tab1, tab2 = st.tabs(["🔥 接案大廳", "✅ 我的任務"])
    
    # --- Tab 1: 接案大廳 (顯示未接案件) ---
    with tab1:
        st.info("這裡顯示目前所有開放中的案件，點擊「立即接案」即可搶單！")
        
        # 尋找所有 status 為 "Open" 的工作
        open_jobs = [j for j in st.session_state.jobs_db if j["status"] == "Open"]
        
        if not open_jobs:
            st.warning("目前沒有新案件，晚點再來看看吧！")
        
        for job in open_jobs:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(job["title"])
                    st.write(f"📅 日期: {job['date']} | 📍 地點: {job['location']}")
                    st.write(f"💰 預算: **{job['budget']}**")
                with c2:
                    st.write("") # 排版用
                    st.write("") 
                    # 接案按鈕
                    if st.button("⚡ 立即接案", key=f"job_{job['id']}"):
                        # 更新資料狀態
                        job["status"] = "Taken"
                        job["taker"] = st.session_state["username"]
                        st.toast(f"恭喜！您已接下【{job['title']}】")
                        time.sleep(1)
                        st.rerun() # 重新整理畫面

    # --- Tab 2: 我的任務 (顯示已接案件) ---
    with tab2:
        my_jobs = [j for j in st.session_state.jobs_db if j["taker"] == st.session_state["username"]]
        
        if not my_jobs:
            st.write("您目前還沒有接案紀錄。")
        else:
            for job in my_jobs:
                with st.container(border=True):
                    st.subheader(f"✅ {job['title']}")
                    st.write(f"📅 {job['date']} | 📍 {job['location']} | 💰 {job['budget']}")
                    st.success("狀態：已確認 (請準時出席)")

def page_user_profile():
    """6. 會員中心"""
    st.header("👤 會員中心")
    st.write(f"調酒師 ID：**{st.session_state['username']}**")
    
    # 統計接案數量
    my_job_count = len([j for j in st.session_state.jobs_db if j["taker"] == st.session_state["username"]])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("會員等級", "黃金調酒師")
    col2.metric("累積接案", f"{my_job_count} 件")
    col3.metric("好評率", "4.9 ⭐")
    
    if st.button("登出系統"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==========================================
# 3. 主程式控制
# ==========================================

# 初始化
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    page_login()
else:
    with st.sidebar:
        st.title("🍹 Bar Master")
        st.write(f"Hi, {st.session_state['username']}")
        
        menu_dict = {
            "📖 酒譜大全": page_recipes,
            "🍋 材料管理": page_ingredients,
            "🧮 濃度計算": page_abv_calculator,
            "🥂 酒杯換算": page_glassware,
            "🍷 醒酒建議": page_decanting,
            "📚 教學資料庫": page_tutorials,   # 新增
            "💼 接案中心": page_job_center,    # 新增
            "👤 會員中心": page_user_profile
        }
        
        choice = st.radio("功能選單", list(menu_dict.keys()))
    
    # 執行對應的頁面函數
    menu_dict[choice]()