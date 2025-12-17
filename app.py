import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Boot Camp Scorecard",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== GOOGLE SHEETS CONFIG ====================
try:
    SHEETS_CREDENTIALS = st.secrets["gcp_service_account"]
    SHEET_ID = st.secrets["sheet_id"]
    use_gsheets = True
except:
    st.warning("⚠️ Google Sheets not configured. Data will be saved locally. (Google Sheets 未設定，數據將儲存在本機)")
    use_gsheets = False

def get_gsheet_client():
    try:
        creds = Credentials.from_service_account_info(
            SHEETS_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return gspread.authorize(creds)
    except:
        return None

# ==================== BOOT CAMP EVALUATION ====================
st.title("🥋 Taekwondo Boot Camp Weekly Evaluation (跆拳道集訓每週評估)")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    athlete_name = st.text_input("Athlete Name (選手名字)", placeholder="e.g., Li Xiaoming")

with col2:
    weight_categories = {
        "Senior (成人)": {
            "Male (男)": ["-54 kg", "-58 kg", "-63 kg", "-68 kg", "-74 kg", "-80 kg", "-87 kg", "+87 kg"],
            "Female (女)": ["-46 kg", "-49 kg", "-53 kg", "-57 kg", "-62 kg", "-67 kg", "-73 kg", "+73 kg"]
        },
        "Junior (青少年 15-17歲)": {
            "Male (男)": ["-45 kg", "-48 kg", "-51 kg", "-55 kg", "-59 kg", "-63 kg", "-68 kg", "-73 kg", "-78 kg", "+78 kg"],
            "Female (女)": ["-42 kg", "-44 kg", "-46 kg", "-49 kg", "-52 kg", "-55 kg", "-59 kg", "-63 kg", "-68 kg", "+68 kg"]
        },
        "Cadet (少年 12-14歲)": {
            "Male (男)": ["-33 kg", "-37 kg", "-41 kg", "-45 kg", "-49 kg", "-53 kg", "-57 kg", "-61 kg", "-65 kg", "+65 kg"],
            "Female (女)": ["-29 kg", "-33 kg", "-37 kg", "-41 kg", "-44 kg", "-47 kg", "-51 kg", "-55 kg", "-59 kg", "+59 kg"]
        }
    }
    
    age_group = st.selectbox("Age Group (年齡組)", 
        ["Senior (成人)", "Junior (青少年 15-17歲)", "Cadet (少年 12-14歲)"])
    
    gender = st.radio("Gender (性別)", ["Male (男)", "Female (女)"], horizontal=True)
    
    weight_class = st.selectbox("Weight Class (量級)", 
        weight_categories[age_group][gender])

with col3:
    pass

col4, col5 = st.columns(2)
with col4:
    bootcamp_name = st.text_input("Boot Camp Name (集訓名稱)", 
        value=f"Boot Camp {datetime.now().strftime('%b %Y')}")
with col5:
    bootcamp_date = st.date_input("Evaluation Date (評估日期)", value=datetime.now())

st.markdown("---")

# ==================== FIVE CORE INDICATORS ====================
st.subheader("📊 Five Core Evaluation Dimensions (五大核心評估指標)")

# 1. Technical & Tactical
with st.expander("1️⃣ Technical & Tactical (技術與戰術)", expanded=True):
    st.write("**Scope:** Pre-match planning, In-match execution, Match control, Opponent style adaptation")
    st.write("**評估範圍:** 賽前規劃、比賽執行、場上控制、對手風格適應")
    technical_score = st.slider(
        "Score (1-5) (評分)",
        1, 5, 3,
        key="technical",
        help="""
        5 = Consistent performance, tactical execution >85% / 五天內表現持續穩定，戰術執行 >85%
        4 = Mostly good, occasional gaps / 多數表現良好，偶有執行偏差
        3 = Average, tactical execution fluctuates / 表現中等，戰術執行有起伏
        2 = Unstable, needs improvement / 執行不穩，需要重點改進
        1 = Fundamental skills insufficient / 基本功不足，需要基礎訓練
        """
    )
    technical_note = st.text_area(
        "Coach Notes (教練觀察)",
        placeholder="Record observations / 記錄重點表現",
        max_chars=100,
        key="technical_note"
    )

# 2. Physical Capacity
with st.expander("2️⃣ Physical Capacity (體能狀態)"):
    st.write("**Scope:** Training completion, late-training skill quality, fatigue recovery, injury risk")
    st.write("**評估範圍:** 訓練完成度、後期技術品質、疲勞恢復、傷病風險")
    physical_score = st.slider(
        "Score (1-5) (評分)",
        1, 5, 3,
        key="physical",
        help="""
        5 = Full attendance, no quality drop, good recovery / 五天全勤，後期技術品質無明顯下降
        4 = Full/nearly full, slight late drop / 全勤或僅1次缺課，後期有輕微品質下降
        3 = >80% attendance, visible fatigue / 出席 >80%，中期明顯疲勞跡象
        2 = Multiple absences, clear decline / 多次缺課或疲勞過度，技術品質明顯衰退
        1 = Cannot complete, injury risk / 無法完成集訓強度，存在傷病風險
        """
    )
    physical_note = st.text_area(
        "Notes - Injury/Fatigue (傷病、疲勞程度等)",
        placeholder="Record physical conditions / 記錄相關狀況",
        max_chars=100,
        key="physical_note"
    )

# 3. Competition Behavior
with st.expander("3️⃣ Competition Behavior (競賽行為)"):
    st.write("**Scope:** Response to scoring, decisions when behind, coach execution, emotional control")
    st.write("**評估範圍:** 失分後反應、落後時決策、教練指令執行、情緒管理")
    behavior_score = st.slider(
        "Score (1-5) (評分)",
        1, 5, 3,
        key="behavior",
        help="""
        5 = Stable response, quick adjustments, good control / 臨場反應穩定，能快速調整，情緒控制好
        4 = Mostly good, occasional overreaction / 多數表現良好，偶有過度反應或延遲調整
        3 = Poor in some, needs reminding / 部分比賽反應不佳，需要提醒才能調整
        2 = Multiple impulsive reactions / 多場比賽出現過度衝動或消極反應
        1 = Unstable, cannot self-adjust / 臨場行為不穩定，無法自主調整
        """
    )
    behavior_note = st.text_area(
        "Key Match Events (關鍵事件記錄)",
        placeholder="Record match behavior / 記錄行為表現或特殊事件",
        max_chars=100,
        key="behavior_note"
    )

# 4. Competition Readiness
with st.expander("4️⃣ Competition Readiness (競賽準備度)"):
    st.write("**Scope:** International standard proximity, opponent adaptation, high-intensity tolerance, international readiness")
    st.write("**評估範圍:** 國際標準接近度、對手風格適應、高強度承受力、國際賽就緒度")
    readiness_score = st.slider(
        "Score (1-5) (評分)",
        1, 5, 3,
        key="readiness",
        help="""
        5 = Fully meets standard, ready / 完全符合國際標準，可直接參賽
        4 = Mostly compliant, minor adjustments / 大部分符合，個別細節需調整
        3 = Near standard, needs 1-2 matches / 接近標準，需要 1-2 場國際賽磨合
        2 = Basic but clear gap, not recommended immediately / 有基礎但差距明顯，不建議立即參賽
        1 = Large gap, needs long-term development / 差距大，需要長期培養
        """
    )
    readiness_note = st.text_area(
        "International Readiness Comment (國際準備度評論)",
        placeholder="Current level vs opponents / 當前水準 vs 國際對手差距",
        max_chars=100,
        key="readiness_note"
    )

# 5. Attendance & Commitment
with st.expander("5️⃣ Attendance & Commitment (出席與投入)"):
    st.write("**Scope:** Attendance rate, key class participation, training attitude, coach cooperation")
    st.write("**評估範圍:** 出席率、關鍵課程參與、訓練態度、與教練配合度")
    attendance_score = st.slider(
        "Score (1-5) (評分)",
        1, 5, 3,
        key="attendance",
        help="""
        5 = 100% attendance, full engagement, proactive / 100% 出席，全程投入，主動配合
        4 = >95% attendance, minor inattention / >95% 出席，僅輕微心不在焉
        3 = 80-95% or engagement fluctuates / 80-95% 出席，或投入度波動
        2 = <80% or clear lack of focus / <80% 出席，或明顯缺乏專注
        1 = Multiple absences, poor attitude / 多次缺課，態度不佳，配合度差
        """
    )
    attendance_note = st.text_area(
        "Attendance Record (出席記錄)",
        placeholder="Absence reasons / 缺課原因、特殊狀況等",
        max_chars=100,
        key="attendance_note"
    )

st.markdown("---")

# ==================== RISK FLAGS ====================
st.subheader("⚠️ Risk Flags (風險標誌)")
risk_cols = st.columns(3)
risks = []

with risk_cols[0]:
    if st.checkbox("Injury Risk (傷病風險)", key="risk_injury"):
        risks.append("Injury Risk")
    if st.checkbox("Overtraining (疲勞過度)", key="risk_fatigue"):
        risks.append("Overtraining")

with risk_cols[1]:
    if st.checkbox("Performance Inconsistency (表現波動)", key="risk_inconsistency"):
        risks.append("Performance Inconsistency")
    if st.checkbox("Poor Decision-Making (決策能力差)", key="risk_decision"):
        risks.append("Poor Decision-Making")

with risk_cols[2]:
    if st.checkbox("Opponent Adaptation Gap (對手適應差)", key="risk_adaptation"):
        risks.append("Opponent Adaptation Gap")
    other_risk = st.text_input("Other Risks (其他風險)", placeholder="Enter if applicable / 如有其他風險請輸入", key="other_risk_input")
    if other_risk:
        risks.append(other_risk)

st.markdown("---")

# ==================== ATHLETE STATUS ====================
st.subheader("🎯 Athlete Status (選手定位)")
status = st.radio(
    "Select Status (選擇定位)",
    ["Ready Now", "Developing", "Re-assess"],
    format_func=lambda x: {
        "Ready Now": "✅ Ready Now ",
        "Developing": "🚀 Developing ",
        "Re-assess": "⚠️ Re-assess "
    }[x]
)

st.markdown("---")

# ==================== KEY TAKEAWAYS ====================
st.subheader("📝 Boot Camp Key Outcomes (重點成果)")

col_top = st.columns(3)

with col_top[0]:
    st.write("**Top 3 Achievements (收穫)**")
    top1 = st.text_input("Achievement 1 ", key="top1")
    top2 = st.text_input("Achievement 2 ", key="top2")
    top3 = st.text_input("Achievement 3 ", key="top3")

with col_top[1]:
    st.write("**Key Improvement Areas **")
    improve1 = st.text_input("Improvement 1 ", key="improve1")
    improve2 = st.text_input("Improvement 2 ", key="improve2")
    improve3 = st.text_input("Improvement 3 ", key="improve3")

with col_top[2]:
    st.write("**Next Steps (4-8 weeksk **")
    action1 = st.text_input("Action 1 ", key="action1")
    action2 = st.text_input("Action 2 ", key="action2")
    action3 = st.text_input("Action 3 ", key="action3")

st.markdown("---")

# ==================== FIVE-DIMENSION RADAR CHART ====================
st.subheader("📊 Five-Dimension Radar Chart ")

scores_dict = {
    "Technical & Tactical": technical_score,
    "Physical Capacity": physical_score,
    "Competition Behavior": behavior_score,
    "Competition Readiness": readiness_score,
    "Attendance & Commitment": attendance_score
}

fig = go.Figure(data=go.Scatterpolar(
    r=list(scores_dict.values()),
    theta=list(scores_dict.keys()),
    fill='toself',
    name=athlete_name if athlete_name else "Athlete",
    line_color='#2080A0',
    fillcolor='rgba(32, 128, 160, 0.5)'
))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
    showlegend=True,
    height=500,
    title=f"Boot Camp Evaluation — {athlete_name or 'Athlete'} ({bootcamp_date})"
)

st.plotly_chart(fig, width='stretch')

# ==================== SUMMARY CARD ====================
st.markdown("---")
st.subheader("📋 Evaluation Summary (評估摘要)")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.metric("Average Score (平均評分)", f"{sum(scores_dict.values()) / 5:.1f} / 5.0")
    st.metric("Strongest Area (最強項)", max(scores_dict, key=scores_dict.get))
    st.metric("Needs Improvement (改進項)", min(scores_dict, key=scores_dict.get))

with summary_col2:
    st.metric("Status (定位)", status)
    st.metric("Risk Count (風險數)", len(risks))
    if risks:
        st.write("**Identified Risks (識別風險):**")
        for risk in risks:
            st.write(f"• {risk}")

st.markdown("---")

# ==================== SAVE OPTIONS ====================
col_save1, col_save2 = st.columns(2)

with col_save1:
    if st.button("💾 Download as CSV (下載評估為 CSV)", width='stretch'):
        data_row = {
            "Timestamp": datetime.now().isoformat(),
            "Athlete Name": athlete_name,
            "Gender": gender,
            "Weight Class": weight_class,
            "Age Group": age_group,
            "Boot Camp Name": bootcamp_name,
            "Boot Camp Date": str(bootcamp_date),
            "Technical & Tactical": technical_score,
            "Physical Capacity": physical_score,
            "Competition Behavior": behavior_score,
            "Competition Readiness": readiness_score,
            "Attendance & Commitment": attendance_score,
            "Status": status,
            "Risks": ", ".join(risks),
            "Technical Note": technical_note,
            "Physical Note": physical_note,
            "Behavior Note": behavior_note,
            "Readiness Note": readiness_note,
            "Attendance Note": attendance_note,
            "Top Achievements": f"{top1} | {top2} | {top3}",
            "Improvements": f"{improve1} | {improve2} | {improve3}",
            "Next Actions": f"{action1} | {action2} | {action3}"
        }
        
        df = pd.DataFrame([data_row])
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Click to Download CSV (點此下載)",
            data=csv,
            file_name=f"bootcamp_{athlete_name}_{bootcamp_date}.csv",
            mime="text/csv"
        )

with col_save2:
    if use_gsheets and st.button("📤 Save to Google Sheets (儲存到 Google Sheets)", width='stretch'):
        try:
            gc = get_gsheet_client()
            ws = gc.open_by_key(SHEET_ID).sheet1
            
            row = [
                datetime.now().isoformat(),
                "Boot Camp",
                athlete_name,
                gender,
                weight_class,
                age_group,
                bootcamp_name,
                str(bootcamp_date),
                technical_score,
                physical_score,
                behavior_score,
                readiness_score,
                attendance_score,
                status,
                ", ".join(risks),
                technical_note,
                physical_note,
                behavior_note,
                readiness_note,
                attendance_note,
                f"{top1} | {top2} | {top3}",
                f"{improve1} | {improve2} | {improve3}",
                f"{action1} | {action2} | {action3}"
            ]
            
            ws.append_row(row)
            st.success("✅ Saved to Google Sheets! (已儲存到 Google Sheets!)")
        except Exception as e:
            st.error(f"❌ Save failed: {e} (儲存失敗)")
