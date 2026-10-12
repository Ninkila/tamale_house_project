import re

import streamlit as st

from src.auth import login_user, register_user

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def show_auth_page():
    st.title("Tamale House Finder")

    page = st.radio("Choose an option", ["Login", "Register"], horizontal=True)

    if page == "Login":
        username = st.text_input("Username or Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    else:
        full_name = st.text_input("Full Name", key="reg_full_name")
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        role = st.selectbox("I am a", ["Tenant", "Landlord"], key="reg_role")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Create Account"):
            username, email = username.strip(), email.strip()

            if not username:
                st.error("Username is required.")
            elif not email:
                st.error("Email is required.")
            elif not EMAIL_RE.match(email):
                st.error("Please enter a valid email address.")
            elif not password:
                st.error("Password is required.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif register_user(username, email, password, role.lower(), full_name.strip() or None):
                st.success("Account created successfully. You can now log in.")
            else:
                st.error("Username or email already exists.")
