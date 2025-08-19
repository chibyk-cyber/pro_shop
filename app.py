import streamlit as st

# ----------------------------
# Setup Background
# ----------------------------
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/wlIFDy0.jpeg"); /* Background */
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.6);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ----------------------------
# User Store (in-memory)
# ----------------------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234", "customer": "abcd"}  # Default users

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------------------
# Auth Pages
# ----------------------------
menu = st.sidebar.radio("Navigation", ["Sign Up", "Login", "Shop"])

# SIGN UP
if menu == "Sign Up":
    st.title("📝 Sign Up")
    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")
    if st.button("Register"):
        if new_user in st.session_state.users:
            st.error("❌ Username already exists, try another one.")
        elif new_user == "" or new_pass == "":
            st.warning("⚠️ Please enter both username and password")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("✅ Account created! Please log in.")

# LOGIN
elif menu == "Login":
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome {username}!")
        else:
            st.error("❌ Invalid username or password")

# SHOP
elif menu == "Shop":
    if st.session_state.logged_in:
        st.title(f"🛒 Welcome, {st.session_state.username}!")

        category = st.sidebar.radio("Choose Category:", ["Clothes", "Generators"])

        if category == "Clothes":
            st.subheader("👕 T-Shirts")
            st.image("https://thevectorlab.com/cdn/shop/products/flat-lay-tee-front-03_5000x.jpg", width=300)
            st.markdown(
                """
                <a href="https://paystack.shop/pay/af5ijd14sl" target="_blank">
                    <button style="background-color:green;color:white;padding:12px 24px;font-size:16px;border-radius:10px;">
                        Buy T-Shirt (₦10,000) 💳
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )

        elif category == "Generators":
            st.subheader("⚡ Generator")
            st.image("https://kjcrm.s3.eu-central-1.amazonaws.com/uploads/34ad52c728c949729301435c94a9c87b.jpg", width=300)
            st.markdown(
                """
                <a href="https://paystack.shop/pay/83og7ge8mt" target="_blank">
                    <button style="background-color:blue;color:white;padding:12px 24px;font-size:16px;border-radius:10px;">
                        Buy Generator (₦150,000) 💳
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("✅ Logged out successfully!")

    else:
        st.warning("⚠️ Please log in first to access the shop.")
