import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from parser import parse_whatsapp_chat
from analysis import (
    get_basic_stats, get_most_active_users, get_busiest_days,
    get_hourly_activity, get_monthly_timeline,
    get_most_common_words, get_emoji_stats, get_user_word_count
)

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# ── STYLES ───────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1B3A6B; }
    .metric-label { font-size: 0.85rem; color: #555; margin-top: 4px; }
    .section-title { font-size: 1.2rem; font-weight: 600; color: #1B3A6B; margin: 20px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────
st.title("💬 WhatsApp Chat Analyzer")
st.markdown("Upload your WhatsApp chat export and get instant insights about your conversations.")
st.markdown("---")

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Upload Chat")
    st.markdown("""
    **How to export your chat:**
    1. Open WhatsApp chat
    2. Tap ⋮ → More → Export Chat
    3. Choose **Without Media**
    4. Upload the `.txt` file here
    """)
    uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

    st.markdown("---")
    if uploaded_file:
        st.success("✅ File uploaded!")

# ── DEMO DATA GENERATOR ──────────────────────────────────────
def generate_demo_data():
    """Generates realistic demo WhatsApp chat data."""
    import random
    from datetime import date, timedelta

    authors = ["Arjun", "Karthik", "Surya", "Vikram", "Ravi"]
    sample_messages = [
        "Hey how are you?", "What's the plan for today?", "Did you see that match?",
        "I'll be there in 10 minutes", "Can you send me the notes?",
        "That's amazing news!", "haha yes exactly", "Let me check and get back to you",
        "Good morning everyone!", "Happy birthday! 🎉", "Are you free this weekend?",
        "I just finished the assignment", "This is so funny 😂", "https://youtube.com/watch?v=xyz",
        "Let's meet at 5pm", "Sure no problem", "What time does it start?",
        "I was thinking the same thing", "Can someone help me with this?", "Done! ✅"
    ]

    rows = []
    start_date = date(2024, 1, 1)
    for i in range(800):
        d = start_date + timedelta(days=random.randint(0, 365))
        h = random.randint(7, 23)
        m = random.randint(0, 59)
        author = random.choice(authors)
        msg = random.choice(sample_messages)
        # randomly add emojis
        if random.random() < 0.15:
            msg += random.choice([" 😂", " 👍", " ❤️", " 🔥", " 😊", " 🎉"])
        rows.append({
            "date": d, "time": f"{h:02d}:{m:02d}", "hour": h,
            "day_name": d.strftime("%A"), "month": d.strftime("%B %Y"),
            "author": author, "message": msg
        })

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

# ── MAIN LOGIC ───────────────────────────────────────────────
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    df = parse_whatsapp_chat(content)
    if df.empty:
        st.error("❌ Could not parse this file. Make sure it's a WhatsApp export .txt file.")
        st.stop()
    mode = "real"
else:
    st.info("👆 Upload your WhatsApp chat to get started — or scroll down to see a **demo** with sample data.")
    if st.button("▶️ Run Demo with Sample Data"):
        df = generate_demo_data()
        mode = "demo"
        st.success("Running with demo data — upload your own chat for real insights!")
    else:
        st.stop()

# ── FILTER BY USER ────────────────────────────────────────────
all_users = ["Everyone"] + sorted(df['author'].unique().tolist())
selected_user = st.selectbox("🔍 Analyze for:", all_users)

if selected_user != "Everyone":
    filtered_df = df[df['author'] == selected_user]
else:
    filtered_df = df

st.markdown("---")

# ── BASIC STATS ───────────────────────────────────────────────
stats = get_basic_stats(filtered_df)
st.markdown('<p class="section-title">📊 Overview</p>', unsafe_allow_html=True)

cols = st.columns(5)
labels = list(stats.keys())
values = list(stats.values())
for i, col in enumerate(cols):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{values[i]:,}</div>
        <div class="metric-label">{labels[i]}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── CHARTS ROW 1 ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-title">👑 Most Active Users</p>', unsafe_allow_html=True)
    active = get_most_active_users(df, top_n=5)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(active['author'], active['count'], color="#1B3A6B")
    ax.set_xlabel("Messages Sent")
    ax.invert_yaxis()
    ax.bar_label(bars, padding=4, fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown('<p class="section-title">📅 Busiest Days of the Week</p>', unsafe_allow_html=True)
    day_counts = get_busiest_days(filtered_df)
    colors = ["#1B3A6B" if v == day_counts.max() else "#A8BFDD" for v in day_counts.values]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(day_counts.index, day_counts.values, color=colors)
    ax.set_ylabel("Messages")
    ax.set_xticks(range(len(day_counts.index)))
    ax.set_xticklabels(day_counts.index, rotation=30, ha='right')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── CHARTS ROW 2 ─────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<p class="section-title">🕐 Activity by Hour</p>', unsafe_allow_html=True)
    hourly = get_hourly_activity(filtered_df)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(hourly.index, hourly.values, alpha=0.4, color="#1B3A6B")
    ax.plot(hourly.index, hourly.values, color="#1B3A6B", linewidth=2)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Messages")
    ax.set_xticks(range(0, 24, 2))
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col4:
    st.markdown('<p class="section-title">📈 Monthly Message Timeline</p>', unsafe_allow_html=True)
    monthly = get_monthly_timeline(filtered_df)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(len(monthly)), monthly['messages'], marker='o', color="#1B3A6B", linewidth=2)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly['month'], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel("Messages")
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── CHARTS ROW 3 ─────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<p class="section-title">💬 Most Common Words</p>', unsafe_allow_html=True)
    words = get_most_common_words(filtered_df, top_n=15)
    if not words.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(words['word'], words['count'], color="#1B3A6B")
        ax.invert_yaxis()
        ax.set_xlabel("Frequency")
        ax.spines[['top', 'right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

with col6:
    st.markdown('<p class="section-title">😂 Most Used Emojis</p>', unsafe_allow_html=True)
    emojis = get_emoji_stats(filtered_df, top_n=8)
    if emojis.empty:
        st.info("No emojis found in this chat.")
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(emojis['emoji'], emojis['count'], color="#1B3A6B")
        ax.invert_yaxis()
        ax.set_xlabel("Times Used")
        ax.spines[['top', 'right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ── AVG WORDS PER MESSAGE ─────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">📝 Average Words per Message (by User)</p>', unsafe_allow_html=True)
avg_words = get_user_word_count(df)
fig, ax = plt.subplots(figsize=(10, 3.5))
bars = ax.bar(avg_words.index, avg_words.values, color="#1B3A6B")
ax.bar_label(bars, padding=3, fontsize=10)
ax.set_ylabel("Avg Words / Message")
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# ── RAW DATA ─────────────────────────────────────────────────
st.markdown("---")
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered_df.head(100), use_container_width=True)

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>Built with Python · Pandas · Matplotlib · Streamlit &nbsp;|&nbsp; "
    "Project by Shahid Siraj S</small></center>",
    unsafe_allow_html=True
)
