import streamlit as st
import yt_dlp
import os
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CORE CONFIG & STEALTH ---
# Is se Streamlit ka apna menu aur branding gayab ho jayegi
st.set_page_config(page_title="Titan Ultra Pro", page_icon="📥", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stApp {
        background: radial-gradient(circle at top, #1e1b4b, #020617);
        color: #f1f5f9;
    }
    .main-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #fbbf24 0%, #3b82f6 100%);
        color: #000 !important;
        border: none;
        padding: 18px;
        font-weight: 900;
        border-radius: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .main-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(to bottom right, #fde047, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STORAGE SETUP ---
DB_PATH = "titan_vault.db"
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS downloads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT, quality TEXT, type TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def log_to_vault(title, quality, m_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO downloads (title, quality, type, date) VALUES (?, ?, ?, ?)",
              (title, quality, m_type, datetime.now().strftime("%d %b, %H:%M")))
    conn.commit()
    conn.close()

init_db()

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>TITAN V11.5</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8;'>Ghost Edition • No Branding • Sami Khan</p>", unsafe_allow_html=True)

tabs = st.tabs(["🚀 EXTRACTOR", "📂 VAULT", "⚙️ SYSTEM"])

with tabs[0]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    url = st.text_input("🔗 MEDIA LINK", placeholder="Paste video link here...")
    
    col1, col2 = st.columns(2)
    with col1:
        m_type = st.selectbox("Format", ["Video (MP4)", "Audio (MP3)"])
    with col2:
        if m_type == "Video (MP4)":
            quality = st.selectbox("Resolution", ["1080p Full HD", "720p HD", "480p SD"])
        else:
            quality = st.selectbox("Bitrate", ["320kbps (Pro)", "128kbps (Standard)"])
    
    if st.button("EXECUTE EXTRACTION"):
        if url:
            # Auto-clean folder before new download to save server space
            for f in os.listdir(DOWNLOAD_DIR):
                try: os.remove(os.path.join(DOWNLOAD_DIR, f))
                except: pass

            with st.status("Engine Warming Up...", expanded=True) as status:
                try:
                    ydl_opts = {
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                        'quiet': True,
                        'no_warnings': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        }
                    }
                    
                    # Agar aapne cookies.txt upload ki hai, toh ye line activate kar dein:
                    if os.path.exists("cookies.txt"):
                        ydl_opts['cookiefile'] = 'cookies.txt'
                    
                    if m_type == "Audio (MP3)":
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': quality.split('k')[0]}]
                    else:
                        res = quality.split('p')[0]
                        ydl_opts['format'] = f'bestvideo[height<={res}]+bestaudio/best/best'
                        ydl_opts['merge_output_format'] = 'mp4'

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        v_title = info.get('title', 'Extracted_Media')
                        file_name = ydl.prepare_filename(info)
                        if m_type == "Audio (MP3)":
                            file_name = file_name.rsplit('.', 1)[0] + ".mp3"

                    with open(file_name, "rb") as f:
                        st.success(f"Successfully Extracted: {v_title}")
                        st.download_button(
                            label="📥 CLICK TO SAVE TO GALLERY",
                            data=f,
                            file_name=os.path.basename(file_name),
                            mime="video/mp4" if m_type == "Video (MP4)" else "audio/mpeg",
                            use_container_width=True
                        )
                    
                    log_to_vault(v_title, quality, m_type)
                    status.update(label="Process Finalized!", state="complete")
                    
                except Exception as e:
                    st.error(f"Engine Alert: {str(e)}")
                    st.info("Tip: If error 403 persists, please upload a fresh cookies.txt to GitHub.")
        else:
            st.warning("Input required.")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT title, quality, type, date FROM downloads ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("System Control")
    st.write("🛡️ Mode: Secure Stealth")
    st.write("🛰️ Server: Frankfurt-01")
    if st.button("🧹 Wipe Vault History"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)