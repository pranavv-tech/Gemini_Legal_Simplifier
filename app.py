import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import sqlite3
import hashlib

# --- CONFIG ---
st.set_page_config(page_title="LegalEase AI", page_icon="⚖️", layout="wide")

# CSS Load (Ensure style.css is in same folder)
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    st.error("style.css file missing!")

# --- DB LOGIC ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()
def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    return c.fetchall()
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- GEMINI SETUP ---
API_KEY = "AIzaSyCU2hYBiaLsrB9tCaLBVff4tm2rGQhKQxI" # <--- Yahan apni key dalo
genai.configure(api_key=API_KEY)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

def main():
    create_usertable()
    
    if not st.session_state['logged_in']:
        # Designing like the REERUI image
        empty_col, main_col, empty_col2 = st.columns([0.2, 1, 0.2])
        
        with main_col:
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            
            # Header
            st.markdown("<h1 style='text-align: left; font-size: 45px;'>Login</h1>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 16px; margin-bottom: 30px;'>Welcome back to your AI legal assistant.</p>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Existing User", "Create Account"])
            
            with tab1:
                user = st.text_input("Username", key="login_user")
                pwd = st.text_input("Password", type='password', key="login_pwd")
                if st.button("LOGIN"):
                    if login_user(user, make_hashes(pwd)):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user
                        st.rerun()
                    else:
                        st.error("Check credentials.")
            
            with tab2:
                new_user = st.text_input("New Username")
                new_pwd = st.text_input("New Password", type='password')
                if st.button("SIGN UP"):
                    add_userdata(new_user, make_hashes(new_pwd))
                    st.success("Account Created! Use 'Existing User' to login.")
            
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Dashboard After Login
        col_title, col_user = st.columns([5, 1])
        with col_user:
            st.markdown(f"**👤 Welcome, {st.session_state['username']}**")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()
        
        st.markdown("# ⚖️ LegalEase Pro: Smart Analysis")
        st.write("---")

        uploaded_file = st.file_uploader("Upload your Contract (PDF)", type="pdf")
        
        if uploaded_file:
            if st.button("START DEEP SCAN"):
                with st.spinner("Gemini is analyzing..."):
                    try:
                        # Logic to handle 404 models
                        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
                        model = genai.GenerativeModel(model_name)
                        
                        pdf_reader = PdfReader(uploaded_file)
                        text = "".join([page.extract_text() for page in pdf_reader.pages])
                        
                        response = model.generate_content(f"Analyze this legal text and give 3 points (Summary, Risks, Action): {text[:10000]}")
                        
                        st.markdown("### 🔍 Analysis Report")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

if __name__ == '__main__':
    main()