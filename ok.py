import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import hashlib
import os
from statsmodels.tsa.arima.model import ARIMA  # ARIMA Model for forecasting

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(page_title="Predictive Healthcare Analytics", layout="wide")

# ----------------- DATABASE & FILE PATH SETUP -----------------
DB_FILE = "vaccination_data.db"
USER_DB = "users.db"
DATASET_PATH = "/Users/pavansappidi/Desktop/TARSS/Tars1/Finaldb.xlsx"

# Function to create database connection
def create_connection(db_path):
    return sqlite3.connect(db_path)

# Function to create user database
def setup_user_database():
    conn = create_connection(USER_DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                      )''')
    conn.commit()
    conn.close()

# Function to create vaccination database
def setup_vaccination_database():
    conn = create_connection(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vaccination_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        STATE TEXT,
                        CITY TEXT,
                        AGE_GROUP TEXT,
                        GENDER TEXT,
                        ETHNICITY TEXT,
                        VACCINATED BOOLEAN,
                        Year INTEGER,
                        DESCRIPTION TEXT
                      )''')
    conn.commit()
    conn.close()

# Function to check if data exists in the table
def is_data_present():
    conn = create_connection(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vaccination_data")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Function to load dataset into the database (only if empty)
def load_data_into_db():
    if not is_data_present():
        if os.path.exists(DATASET_PATH):
            df = pd.read_excel(DATASET_PATH)  # Load from the specified path
            conn = create_connection(DB_FILE)
            df.to_sql("vaccination_data", conn, if_exists="replace", index=False)
            conn.close()
            print("✅ Data loaded into the database successfully!")
        else:
            print("❌ Error: File not found at the specified path!")

# Initialize databases
setup_user_database()
setup_vaccination_database()
load_data_into_db()

# ----------------- USER AUTHENTICATION SYSTEM -----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if a user exists in the database
def user_exists(username):
    conn = create_connection(USER_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to add a new user to the database
def add_user(username, password):
    conn = create_connection(USER_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# Function to verify login credentials
def authenticate_user(username, password):
    conn = create_connection(USER_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = cursor.fetchone()
    conn.close()
    if stored_password and stored_password[0] == hash_password(password):
        return True
    return False

# ----------------- LOGIN & SIGNUP PAGES -----------------
def login_page():
    st.title("🔑 Secure Login")
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")

    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state["signup"] = True
        st.experimental_rerun()

def signup_page():
    st.title("📝 Create a New Account")
    new_username = st.text_input("👤 Choose a Username")
    new_password = st.text_input("🔑 Choose a Password", type="password")
    confirm_password = st.text_input("🔑 Confirm Password", type="password")

    if st.button("Sign Up"):
        if new_password != confirm_password:
            st.error("❌ Passwords do not match. Try again.")
        elif user_exists(new_username):
            st.error("❌ Username already exists. Try a different one.")
        else:
            if add_user(new_username, new_password):
                st.success("✅ Account created successfully! You can now log in.")
                st.session_state["signup"] = False
                st.experimental_rerun()
            else:
                st.error("❌ Something went wrong. Try again.")

    st.write("Already have an account?")
    if st.button("Go to Login"):
        st.session_state["signup"] = False
        st.experimental_rerun()

# ----------------- AUTHENTICATION LOGIC -----------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "signup" not in st.session_state:
    st.session_state["signup"] = False

if not st.session_state["authenticated"]:
    if st.session_state["signup"]:
        signup_page()
    else:
        login_page()
    st.stop()

# ----------------- MAIN DASHBOARD -----------------
st.title("📊 Predictive Healthcare Analytics for Vaccine Administration")

# Logout Button
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.experimental_rerun()

# ----------------- FETCH DATA FROM DATABASE -----------------
conn = create_connection(DB_FILE)
df = pd.read_sql("SELECT * FROM vaccination_data", conn)
conn.close()

st.write("### 🔍 Raw Data Preview")
st.dataframe(df.head())

# ----------------- ADD FILTERS -----------------
st.sidebar.header("🔍 Filter Data")
state = st.sidebar.selectbox("📍 Select State", df["STATE"].dropna().unique())
city = st.sidebar.selectbox("🏙 Select City", df[df["STATE"] == state]["CITY"].dropna().unique())

# Multi-select for vaccine types
vaccine_options = df["DESCRIPTION"].dropna().unique()
selected_vaccines = st.sidebar.multiselect("💉 Select Vaccine Type(s)", vaccine_options, default=vaccine_options)

# Filter data based on selections
filtered_df = df[(df["STATE"] == state) & (df["CITY"] == city) & (df["DESCRIPTION"].isin(selected_vaccines))]

# Display filtered data
st.write(f"## 📊 Data for {city}, {state}")
st.dataframe(filtered_df)

# ----------------- TREND ANALYSIS -----------------

::contentReference[oaicite:2]{index=2}
 
