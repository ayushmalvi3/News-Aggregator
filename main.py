import streamlit as st
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import base64
import json

# ---------- Page Setup ----------
st.set_page_config(page_title="News Aggregator", page_icon="📰", layout="wide")

# ---------- Gemini API Key ----------
GEMINI_API_KEY = "AIzaSyB76Sxa67PR7IGbHPs72eCVloU6y2AkYQA"  # Replace with your actual API key

# ---------- Background Image ----------
with open("background.png", "rb") as f:
    b64_bg = base64.b64encode(f.read()).decode()

# ---------- Style ----------
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stAppViewContainer"] {{
        background-color: rgba(0,0,0,0.6);
    }}
    .settings {{
        font-size: 28px;
        color: white;
        padding-right: 20px;
        text-align: right;
    }}
    .chat-box {{
        padding: 15px;
        border: 2px solid white;
        border-radius: 10px;
        background-color: black;
        color: #00FFFF;
        font-size: 16px;
        margin-top: 20px;
        white-space: pre-wrap;
    }}
    .chat-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .chat-header h2 {{
        color: white;
    }}
    .read-button {{
        background-color: black;
        color: #39FF14;
        font-size: 16px;
        padding: 6px 14px;
        border: 2px solid #39FF14;
        border-radius: 5px;
        cursor: pointer;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------- Top Bar ----------
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.jpg", width=100)
with col2:
    st.markdown("<div class='settings'>⚙️</div>", unsafe_allow_html=True)

# ---------- Centered news_img.png ----------
with open("news_img.png", "rb") as img_file:
    img_data = base64.b64encode(img_file.read()).decode()

st.markdown(f"""
    <div style='display: flex; justify-content: center; margin-top: 20px;'>
        <img src="data:image/png;base64,{img_data}" style="width: 500px; border-radius: 10px;" />
    </div>
""", unsafe_allow_html=True)

# ---------- Layout ----------
left_col, right_col = st.columns([1, 5])

# ---------- Sidebar Buttons ----------
with left_col:
    st.markdown("### 📰 News Options")

    if st.button("📌 Today's Headlines"):
        st.session_state.chat_trigger = "What are today's top news headlines in India?"

    if st.button("⭐ Special News"):
        st.session_state.chat_trigger = "What are some special or viral news stories right now?"

    if st.button("🤖 Suggested News"):
        st.session_state.chat_trigger = "Can you suggest some trending topics for news readers?"

    if st.button("🏏 Sport News"):
        st.session_state.chat_trigger = "Give me the latest sports news."

    if st.button("🏛️ Political News"):
        st.session_state.chat_trigger = "What's the latest in Indian politics?"

    if st.button("🪖 Military News"):
        st.session_state.chat_trigger = "Tell me the latest updates on military and defence news in India."

# ---------- Main Content ----------
with right_col:
    st.write("## Select the Date:")
    year_col, month_col, day_col = st.columns(3)

    today = datetime.today()
    default_year = str(today.year)
    default_month = today.strftime("%B").lower()
    default_day = str(today.day)

    year_options = ["2025", "2024", "2023", "2022"]
    year_index = year_options.index(default_year) if default_year in year_options else 0
    year_select = year_col.selectbox("Year", year_options, index=year_index)

    month_options = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    month_index = month_options.index(default_month)
    month_select = month_col.selectbox("Month", month_options, index=month_index)

    day_options = [str(i) for i in range(1, 32)]
    day_index = int(default_day) - 1
    day_select = day_col.selectbox("Day", day_options, index=day_index)

    toggle_btn = st.toggle("Show in Hindi")
    scrap_btn = st.button("Fetch News")

    str_date = str(day_select)
    if str_date.endswith("1") and str_date != "11":
        st.write(f"### News for {day_select}st {month_select}, {year_select}")
    elif str_date.endswith("2") and str_date != "12":
        st.write(f"### News for {day_select}nd {month_select}, {year_select}")
    elif str_date.endswith("3") and str_date != "13":
        st.write(f"### News for {day_select}rd {month_select}, {year_select}")
    else:
        st.write(f"### News for {day_select}th {month_select}, {year_select}")

    box_style = """
        <style>
            .custom-box {
                padding: 10px;
                border: 2px solid white;
                border-radius: 10px;
                background-color: black;
                color: white;
                margin-bottom: 10px;
            }
            .custom-box a {
                color: #00FFFF !important;
                text-decoration: none !important;
                font-weight: bold !important;
            }
        </style>
    """

    if scrap_btn:
        text_language = "2" if toggle_btn else "1"
        url = f"https://sarkaripariksha.com/gk-and-current-affairs/{year_select}/{month_select}/{day_select}/{text_language}/"
        try:
            req = requests.get(url)
            soup = BeautifulSoup(req.text, "html.parser")
            news_list = soup.find_all("div", class_="examlist-details-img-box")
            if not news_list:
                st.warning("⚠️ No news found for this date.")
            else:
                st.markdown(box_style, unsafe_allow_html=True)
                for idx, item in enumerate(news_list, 1):
                    a_tag = item.find("h2").find("a")
                    title = a_tag.get_text(strip=True)
                    link = a_tag["href"]
                    st.markdown(
                        f"""<div class="custom-box">{idx}- <a href="{link}">{title}</a></div>""",
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"❌ Error fetching news: {e}")

# ---------- Gemini AI Chatbot ----------
st.markdown("---")

# Chatbot header with right-aligned Read Aloud
st.markdown(f"""
    <div class="chat-header">
        <h2>🤖 Chat with पत्रकार AI</h2>
        <form action="" method="post">
            <button type="submit" name="read_aloud" class="read-button">🔊 Read Aloud</button>
        </form>
    </div>
""", unsafe_allow_html=True)

# Text input and chatbot
user_input = st.text_input("Ask something about the news or anything:")

# Compose query with language preference
base_query = user_input or st.session_state.get("chat_trigger", "")
if toggle_btn and base_query:
    query = f"{base_query} (Please reply in Hindi)"
else:
    query = base_query

# Fetch Gemini response
if query:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"parts": [{"text": query}]}
            ]
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            result = response.json()
            reply = result['candidates'][0]['content']['parts'][0]['text']

            # Display reply
            st.markdown(f"<div class='chat-box'><strong>Gemini:</strong><br>{reply}</div>", unsafe_allow_html=True)

            # Trigger speech if Read Aloud was clicked
            if "read_aloud" in st.session_state or st.query_params.get("read_aloud"):
                lang = "hi-IN" if toggle_btn else "en-US"
                st.markdown(f"""
                    <script>
                        const msg = new SpeechSynthesisUtterance(`{reply}`);
                        msg.lang = "{lang}";
                        msg.pitch = 1;
                        msg.rate = 1;
                        window.speechSynthesis.speak(msg);
                    </script>
                """, unsafe_allow_html=True)

        else:
            st.error(f"❌ Gemini API Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"❌ Exception while calling Gemini API: {e}")

    st.session_state.chat_trigger = ""
