import streamlit as st

# -------------------
# Set Background Image
# -------------------
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/wlIFDy0.jpeg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    color: white;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.5);
    color: white;
}

button, .stButton>button {
    background-color: rgba(0, 128, 0, 0.8) !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# -------------------
# Simple Login
# -------------------
users = {"admin": "1234", "customer": "abcd"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔑 Login to Shop")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid username or password")

else:
    st.title("🛒 Welcome to Petrosini Global Investment")

    # -------------------
    # Category Selection
    # -------------------
    category = st.radio("Select a category", ["Clothes", "Generators"])

    if category == "Clothes":
        st.subheader("👕 Clothes")
        st.image("https://i.imgur.com/oZ6w0.jpg", width=200)
        if st.button("Buy T-Shirt (₦10,000)"):
            st.markdown(
                """
                <a href="https://paystack.shop/pay/af5ijd14sl" target="_blank">
                    <button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button>
                </a>
                """,
                unsafe_allow_html=True
            )

    elif category == "Generators":
        st.subheader("⚡ Generators")
        st.image("https://i.imgur.com/LiJ0v.jpg", width=200)
        if st.button("Buy Generator (₦150,000)"):
            st.markdown(
                """
                <a href="https://paystack.shop/pay/83og7ge8mt" target="_blank">
                    <button style="background-color:blue;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button>
                </a>
                """,
                unsafe_allow_html=True
            )

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()



