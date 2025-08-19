import streamlit as st

# ===========================
# Petrosini Global Investment - Company Shop
# Auth-first → Sidebar Navigation → Shop (Clothes & Generators) → Contact Us → Logout
# ===========================

# -------------------
# Styling (Background + Footer)
# -------------------
PAGE_BG = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/wlIFDy0.jpeg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background-color: rgba(0,0,0,0.6); color: white; }

/**** Text color tweak for dark bg ****/
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: white !important; }

/* Footer */
.footer { position: fixed; left: 0; bottom: 0; width: 100%;
          background-color: rgba(0,0,0,0.75); color: white; text-align: center;
          padding: 10px; font-size: 14px; z-index: 9999; }

/* Product cards */
.card { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
        border-radius: 14px; padding: 14px; }
.card h4 { margin: 6px 0 8px 0; }
.buybtn { display: inline-block; padding: 10px 16px; border-radius: 10px;
          text-decoration: none; font-weight: 600; }
.buy-green { background:#1aa251; color:white; }
.buy-blue  { background:#2563eb; color:white; }
.buy-purple{ background:#7c3aed; color:white; }
.buy-orange{ background:#ea580c; color:white; }
.buy-red   { background:#dc2626; color:white; }
</style>
"""
st.markdown(PAGE_BG, unsafe_allow_html=True)

# -------------------
# Session State (Users & Auth)
# -------------------
if "users" not in st.session_state:
    # Default demo users; you can preload more here
    st.session_state.users = {"admin": "1234", "customer": "abcd"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "Login"  # or "Sign Up"

# -------------------
# AUTH FIRST (Sign Up / Login)
# -------------------
if not st.session_state.logged_in:
    st.title("🔐 Petrosini Global Investment")
    st.subheader("Please sign in or create an account to continue")

    view = st.radio("Authentication", ["Login", "Sign Up"], index=0 if st.session_state.auth_view=="Login" else 1, horizontal=True)
    st.session_state.auth_view = view

    if view == "Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password")

    else:  # Sign Up
        new_user = st.text_input("Choose a Username", key="su_user")
        new_pass = st.text_input("Choose a Password", type="password", key="su_pass")
        confirm  = st.text_input("Confirm Password", type="password", key="su_conf")
        if st.button("Create Account"):
            if not new_user or not new_pass or not confirm:
                st.warning("⚠️ Please fill all fields")
            elif new_user in st.session_state.users:
                st.error("❌ Username already exists. Choose another.")
            elif new_pass != confirm:
                st.error("❌ Passwords do not match")
            elif len(new_pass) < 4:
                st.warning("⚠️ Use a password of at least 4 characters for this demo")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("✅ Account created! Please log in.")
                st.session_state.auth_view = "Login"
                st.experimental_rerun()

# -------------------
# AFTER LOGIN → SIDEBAR NAV
# -------------------
else:
    page = st.sidebar.radio("📍 Navigate", ["🏠 Home", "🛍️ Shop", "📩 Contact Us", "🚪 Logout"])  

    # HOME
    if page == "🏠 Home":
        st.title("🏢 Welcome to Petrosini Global Investment")
        st.write(
            "We sell quality **clothes, generators, and power accessories** at fair prices. "
            "Secure checkout powered by **Paystack**."
        )

    # SHOP
    elif page == "🛍️ Shop":
        st.title("🛍️ Our Products")
        category = st.selectbox("Choose Category", ["Clothes", "Generators"])  

        if category == "Clothes":
            st.subheader("👗 Clothes Collection")
            col1, col2, col3 = st.columns(3)

            # Gowns
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image("https://i.imgur.com/NTpQO3H.jpeg", use_container_width=True)
                st.markdown("<h4>Elegant Gown</h4><p>₦15,000</p>", unsafe_allow_html=True)
                st.markdown(
                    '<a class="buybtn buy-green" href="https://paystack.shop/pay/ytcdggzv02" target="_blank">Buy with Paystack 💳</a>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # Wrappers (making clothes)
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image("https://i.imgur.com/tKE4gOv.jpeg", use_container_width=True)
                st.markdown("<h4>Wrapper (Making Clothes)</h4><p>₦10,000</p>", unsafe_allow_html=True)
                st.markdown(
                    '<a class="buybtn buy-blue" href="https://paystack.shop/pay/af5ijd14sl" target="_blank">Buy with Paystack 💳</a>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # Powerbanks
            with col3:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image("https://i.imgur.com/pHvvqXJ.jpeg", use_container_width=True)
                st.markdown("<h4>High-Capacity Powerbank</h4><p>₦8,000</p>", unsafe_allow_html=True)
                st.markdown(
                    '<a class="buybtn buy-purple" href="https://paystack.shop/pay/duq9rhs4m5" target="_blank">Buy with Paystack 💳</a>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

        else:  # Generators
            st.subheader("⚡ Generators")
            colg1, colg2, colg3 = st.columns(3)
            with colg1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image("https://i.imgur.com/Y8j1gY2.jpeg", use_container_width=True)
                st.markdown("<h4>Portable Generator</h4><p>₦150,000</p>", unsafe_allow_html=True)
                st.markdown(
                    '<a class="buybtn buy-orange" href="https://paystack.shop/pay/83og7ge8mt" target="_blank">Buy with Paystack 💳</a>',
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)
            # (Optional) Add more generator cards here later

    # CONTACT US
    elif page == "📩 Contact Us":
        st.title("📩 Contact Us")
        st.write("Have questions or want to place a custom order? Fill out the form, or reach us directly:")
        st.markdown("**Phone:** 07030215269  ")
        st.markdown("**Email:** obichibuikegoodluck@gmail.com")

        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            phone = st.text_input("Your Phone Number")
            message = st.text_area("Your Message")
            submitted = st.form_submit_button("Send Message ✉️")

            if submitted:
                if name and email and phone and message:
                    st.success(
                        f"✅ Thank you {name}! Your message has been received.\n\n"
                        f"We’ll reach you at 📞 {phone} or 📧 {email}."
                    )
                else:
                    st.error("⚠️ Please fill in all fields before submitting.")

    # LOGOUT
    elif page == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    # FOOTER (always visible after login)
    st.markdown(
        """
        <div class="footer">
            📞 Contact us: <b>07030215269</b> &nbsp;|&nbsp; 📧 <b>obichibuikegoodluck@gmail.com</b> &nbsp;|&nbsp; © 2025 Petrosini Global Investment
        </div>
        """,
        unsafe_allow_html=True,
    )
