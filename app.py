import streamlit as st
import yt_dlp
import os
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CORE ENGINE & DB ---
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

# --- 2. LUXURY BLACK GOLD UI ---
st.set_page_config(page_title="Titan Ultra Pro v11", page_icon="📥", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1e1b4b, #020617);
        color: #f1f5f9;
    }
    /* Glassmorphism Card */
    .main-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    /* Gold & Blue Gradient Button */
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
        transition: 0.4s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.6);
        transform: scale(1.02);
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(to bottom right, #fde047, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .stTextInput>div>div>input {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #fbbf24 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC & DOWNLOADER ---
st.markdown("<h1 class='main-title'>TITAN V11</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-weight:bold;'>ENTERPRISE MEDIA EXTRACTOR</p>", unsafe_allow_html=True)

tabs = st.tabs(["🚀 MASTER ENGINE", "📂 VAULT", "⚙️ SYSTEM"])

with tabs[0]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    url = st.text_input("🔗 MEDIA LINK", placeholder="Paste YouTube, Facebook, or Twitter URL...")
    
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
            with st.status("Engine Warming Up...", expanded=True) as status:
                try:
                    # Anti-Block Stealth Config
                    ydl_opts = {
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                        'quiet': True,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        }
                    }
                    
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

                    # THE MASTER UPGRADE: Direct Save to Device
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
        else:
            st.warning("Input required.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: VAULT ---
with tabs[1]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT title, quality, type, date FROM downloads ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: SYSTEM ---
with tabs[2]:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Cloud Control")
    st.write("🛰️ Server: Frankfurt-01")
    if st.button("🧹 Clear Server Storage"):
        for f in os.listdir(DOWNLOAD_DIR):
            os.remove(os.path.join(DOWNLOAD_DIR, f))
        st.success("Storage Purged.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:#475569; font-size:0.8rem; margin-top:50px;'>TITAN CORE v11.0 • Sami Khan</p>", unsafe_allow_html=True)