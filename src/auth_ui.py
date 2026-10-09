import streamlit as st
import re
from src.auth import login_user, register_user


def show_auth_page():
    st.title("Tamale House Finder")

    page = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True
    )

    if page == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    else:
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Create Account"):
            if not username.strip():
                st.error("Username is required.")

            elif not email.strip():
                st.error("Email is required.")

            elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                st.error("Please enter a valid email address.")

            elif not password:
                st.error("Password is required.")

            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:
                result = register_user(username, email, password)

                if result:
                    st.success(
                        "Account created successfully. You can now log in."
                    )
                else:
                    st.error("Username or email already exists.")