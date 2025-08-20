import streamlit as st
from datetime import datetime

# -----------------------------
# Initialize session state
# -----------------------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}  # default user
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -----------------------------
# Sign Up Page
# -----------------------------
def signup():
    st.title("📝 Sign Up")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")

    if st.button("Create Account"):
        if new_user in st.session_state.users:
            st.error("⚠️ Username already exists. Try another.")
        elif new_user.strip() == "" or new_pass.strip() == "":
            st.error("⚠️ Username and password cannot be empty.")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("✅ Account created successfully! Please go to Login.")

# -----------------------------
# Login Page
# -----------------------------
def login():
    st.title("🔑 Login to Shop")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success(f"✅ Welcome {username}!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# -----------------------------
# Shop Page
# -----------------------------
def shop():
    st.title("🛒 Welcome to My Company Shop")

    menu = ["Clothes", "Generators", "Contact Us"]
    choice = st.sidebar.radio("📂 Categories", menu)

    # CLOTHES SECTION
    if choice == "Clothes":
        st.subheader("👕 Clothes Section")
        sub = st.selectbox("Choose a product:", ["Gowns", "Wrappers", "Powerbanks"])

        if sub == "Gowns":
            st.image("https://cdn.shopify.com/s/files/1/0253/6561/0601/products/robe1.jpg", width=250)
            if st.button("Buy Gown (₦15,000)"):
                st.markdown('<a href="https://paystack.shop/pay/ytcdggzv02" target="_blank"><button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button></a>', unsafe_allow_html=True)

        elif sub == "Wrappers":
            st.image("https://i.imgur.com/oZ6w0.jpg", width=250)
            if st.button("Buy Wrapper (₦10,000)"):
                st.markdown('<a href="https://paystack.shop/pay/af5ijd14sl" target="_blank"><button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button></a>', unsafe_allow_html=True)

        elif sub == "Powerbanks":
            st.image("https://i.imgur.com/1ZQZ1Zm.jpg", width=250)
            if st.button("Buy Powerbank (₦20,000)"):
                st.markdown('<a href="https://paystack.shop/pay/duq9rhs4m5" target="_blank"><button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button></a>', unsafe_allow_html=True)

    # GENERATORS SECTION
    elif choice == "Generators":
        st.subheader("⚡ Generators Section")
        st.image("https://i.imgur.com/LiJ0v.jpg", width=250)
        if st.button("Buy Generator (₦150,000)"):
            st.markdown('<a href="https://paystack.shop/pay/83og7ge8mt" target="_blank"><button style="background-color:blue;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button></a>', unsafe_allow_html=True)

    # CONTACT US PAGE
    elif choice == "Contact Us":
        st.subheader("📞 Contact Us")
        st.write("Have issues signing in or buying?")
        st.write("📧 Email: **obichibuikegoodluck@gmail.com**")
        st.write("📱 Phone: **07030215269**")
        st.write("🕒 Support Hours: Mon - Sat (9am - 6pm)")

    # Logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

# -----------------------------
# MAIN APP CONTROLLER
# -----------------------------
def main():
    if not st.session_state.logged_in:
        page = st.sidebar.radio("Navigation", ["Login", "Sign Up"])
        if page == "Login":
            login()
        else:
            signup()
    else:
        shop()

if __name__ == "__main__":
    main()
