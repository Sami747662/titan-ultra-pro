import streamlit as st
import yt_dlp
import os
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CORE ENGINE & DB ---
DB_PATH = "titan_vault.db"

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

# --- 2. LUXURY GLASS UI ---
st.set_page_config(page_title="Titan v9.0", page_icon="📥", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: #0f172a;
        color: #f1f5f9;
    }
    /* Glass Card Effect */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    /* Glowing Input */
    .stTextInput>div>div>input {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #38bdf8 !important;
        border-radius: 10px !important;
    }
    /* Action Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        color: white;
        border: none;
        padding: 15px;
        font-weight: 800;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(to right, #38bdf8, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>TITAN EXTRACTOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8;'>Advanced Video & Audio Mastering Engine</p>", unsafe_allow_html=True)

tabs = st.tabs(["⚡ Download", "📂 Vault", "⚙️ Config"])

# --- TAB 1: DOWNLOADER ---
with tabs[0]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    url = st.text_input("🔗 Media URL", placeholder="Paste YouTube, Facebook, or Twitter link...")
    
    col1, col2 = st.columns(2)
    with col1:
        m_type = st.selectbox("Media Type", ["Video (MP4)", "Audio (MP3)"])
    with col2:
        if m_type == "Video (MP4)":
            quality = st.selectbox("Resolution", ["4K / 2160p", "2K / 1440p", "1080p Full HD", "720p HD", "480p SD"])
        else:
            quality = st.selectbox("Audio Bitrate", ["320kbps (Studio)", "192kbps (High)", "128kbps (Standard)"])
    
    save_path = st.text_input("💾 Save to", value=os.path.join(os.path.expanduser('~'), 'Downloads', 'Titan'))
    
    if st.button("EXECUTE EXTRACTION"):
        if url:
            with st.status("Engine Warming Up...", expanded=True) as status:
                try:
                    # Logic Setup
                    ydl_opts = {
                        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                        'quiet': True,
                        'no_warnings': True,
                    }
                    
                    if m_type == "Audio (MP3)":
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': quality.split('k')[0],
                        }]
                    else:
                        res = quality.split(' / ')[1].replace('p', '') if ' / ' in quality else quality.split('p')[0]
                        ydl_opts['format'] = f'bestvideo[height<={res}]+bestaudio/best/best'
                        ydl_opts['merge_output_format'] = 'mp4'

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        v_title = info.get('title', 'Unknown Media')
                        st.image(info.get('thumbnail'), caption=v_title, width=400)
                    
                    log_to_vault(v_title, quality, m_type)
                    status.update(label="Extraction Complete!", state="complete")
                    st.success(f"Saved: {v_title}")
                except Exception as e:
                    st.error(f"Engine Alert: {str(e)}")
        else:
            st.warning("Please provide a valid URL.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: VAULT (HISTORY) ---
with tabs[1]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT title, quality, type, date FROM downloads ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Vault is empty. Start downloading to see history.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: CONFIG ---
with tabs[2]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Engine Preferences")
    st.toggle("Auto-merge Streams (FFmpeg)", value=True)
    st.toggle("Hardware Acceleration (GPU)", value=True)
    st.divider()
    if st.button("🗑️ Clear Vault History"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<p style='text-align:center; color:#475569; font-size:0.8rem;'>TITAN CORE v9.0 • PRO GRADE</p>", unsafe_allow_html=True)