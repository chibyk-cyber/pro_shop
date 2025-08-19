import streamlit as st

# -------------------
# Background Image
# -------------------
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/wlIFDy0.jpeg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stSidebar"] {
    background-color: rgba(0,0,0,0.5);
    color: white;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# -------------------
# Users (Sign In / Login System)
# -------------------
users = {"admin": "1234", "customer": "abcd"}  # example users

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔑 Login to Petrosini Global Investment")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid username or password")

    # Help note for login issues
    st.info("ℹ️ Having trouble signing in? Contact us at 📞 07030215269 or 📧 obichibuikegoodluck@gmail.com")

else:
    # -------------------
    # Sidebar Navigation
    # -------------------
    menu = ["🏠 Home", "👕 Clothes", "⚡ Generators", "📞 Contact Us", "🚪 Logout"]
    choice = st.sidebar.selectbox("Navigate", menu)

    if choice == "🏠 Home":
        st.title("🛒 Welcome to Petrosini Global Investment")
        st.write("We sell quality **Clothes** and **Generators**. Choose a category from the sidebar to start shopping!")

    elif choice == "👕 Clothes":
        st.title("👕 Clothes Section")

        sub_choice = st.radio("Select a subcategory:", ["👗 Gowns", "🧣 Wrappers", "🔋 Powerbanks"])

        if sub_choice == "👗 Gowns":
            st.image("https://i.imgur.com/oZ6w0.jpg", width=200)
            st.markdown(
                """
                <a href="https://paystack.shop/pay/ytcdggzv02" target="_blank">
                    <button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Buy Gown 💳</button>
                </a>
                """,
                unsafe_allow_html=True
            )

        elif sub_choice == "🧣 Wrappers":
            st.image("https://i.imgur.com/9zAqT0N.jpg", width=200)
            st.markdown(
                """
                <a href="https://paystack.shop/pay/af5ijd14sl" target="_blank">
                    <button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Buy Wrapper 💳</button>
                </a>
                """,
                unsafe_allow_html=True
            )

        elif sub_choice == "🔋 Powerbanks":
            st.image("https://i.imgur.com/LIYktjN.jpg", width=200)
            st.markdown(
                """
                <a href="https://paystack.shop/pay/duq9rhs4m5" target="_blank">
                    <button style="background-color:green;color:white;padding:10px 20px;font-size:16px;">Buy Powerbank 💳</button>
                </a>
                """,
                unsafe_allow_html=True
            )

    elif choice == "⚡ Generators":
        st.title("⚡ Generator Section")
        st.image("https://i.imgur.com/LiJ0v.jpg", width=250)
        st.markdown(
            """
            <a href="https://paystack.shop/pay/83og7ge8mt" target="_blank">
                <button style="background-color:blue;color:white;padding:10px 20px;font-size:16px;">Buy Generator 💳</button>
            </a>
            """,
            unsafe_allow_html=True
        )

    elif choice == "📞 Contact Us":
        st.title("📞 Contact Us")
        st.write("If you have any issues or inquiries, reach us via:")
        st.write("📞 Phone: **07030215269**")
        st.write("📧 Email: **obichibuikegoodluck@gmail.com**")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.success("✅ You have been logged out.")
        st.experimental_rerun()
