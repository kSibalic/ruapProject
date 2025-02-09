# authentication.py
import streamlit as st
import pandas as pd
import os

USERS_FILE = "users.csv"

def load_users():
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        return dict(zip(users_df["username"], users_df["password"]))
    else:
        return {}

def save_user(username, password):
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    if os.path.exists(USERS_FILE):
        new_user.to_csv(USERS_FILE, mode="a", index=False, header=False)
    else:
        new_user.to_csv(USERS_FILE, mode="w", index=False, header=True)

def login_signup():
    st.sidebar.title("User Authentication")
    auth_mode = st.sidebar.radio("Select Option", ["Login", "Sign Up"])

    if auth_mode == "Login":
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Log In"):
            users = load_users()
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.sidebar.success(f"Logged in as {username}")
            else:
                st.sidebar.error("Invalid username or password")

    elif auth_mode == "Sign Up":
        new_username = st.sidebar.text_input("New Username", key="signup_username")
        new_password = st.sidebar.text_input("New Password", type="password", key="signup_password")
        new_password_confirm = st.sidebar.text_input("Confirm Password", type="password", key="signup_password_confirm")
        if st.sidebar.button("Sign Up"):
            if new_password != new_password_confirm:
                st.sidebar.error("Passwords do not match")
            else:
                users = load_users()
                if new_username in users:
                    st.sidebar.error("Username already exists")
                else:
                    save_user(new_username, new_password)
                    st.session_state.authenticated = True
                    st.session_state.username = new_username
                    st.sidebar.success(f"Account created and logged in as {new_username}")
