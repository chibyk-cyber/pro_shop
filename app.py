import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json
import re
from datetime import datetime
import extra_streamlit_components as stx

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
    background-color: rgba(0,0,0,0.8);
    color: white;
    padding: 20px;
}

button, .stButton>button {
    background-color: rgba(0, 128, 0, 0.8) !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover, .stButton>button:hover {
    background-color: rgba(0, 100, 0, 1) !important;
    transform: scale(1.05);
}

.auth-container {
    background-color: rgba(0, 0, 0, 0.7);
    padding: 30px;
    border-radius: 15px;
    width: 400px;
    margin: 50px auto;
    box-shadow: 0 8px 16px rgba(0,0,0,0.5);
}

.logout-container {
    background-color: rgba(0, 0, 0, 0.7);
    padding: 20px;
    border-radius: 15px;
    width: 300px;
    margin: 20px auto;
    text-align: center;
}

.stTextInput>div>div>input {
    background-color: rgba(255, 255, 255, 0.9);
    color: black;
}

.tab-container {
    background-color: rgba(0, 0, 0, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
}

.admin-panel {
    background-color: rgba(139, 0, 0, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
}

.user-panel {
    background-color: rgba(0, 100, 0, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
}

</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# -------------------
# Load/Save User Data
# -------------------
def load_users():
    try:
        with open('users.yaml', 'r') as file:
            return yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Default users with hashed passwords
        default_users = {
            'usernames': {
                'admin': {
                    'email': 'admin@petrosini.com',
                    'name': 'System Administrator',
                    'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # hashed "1234"
                    'role': 'admin',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_login': None
                },
                'customer': {
                    'email': 'customer@example.com',
                    'name': 'Valued Customer',
                    'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # hashed "abcd"
                    'role': 'customer',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_login': None
                }
            }
        }
        save_users(default_users)
        return default_users

def save_users(users):
    with open('users.yaml', 'w') as file:
        yaml.dump(users, file)

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

# Load users
credentials = load_users()

# Create authenticator object
authenticator = stauth.Authenticate(
    credentials['usernames'],
    'petrosini_auth',
    'petrosini_auth_key',
    cookie_expiry_days=7
)

# -------------------
# Authentication Flow
# -------------------
# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Main app logic
if not st.session_state.get('authentication_status'):
    # Show login/register tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔒 Forgot Password"])
    
    with tab1:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("🔑 Login to Shop")
        
        try:
            username, authentication_status, password = authenticator.login('Login', 'main')
            
            if authentication_status:
                st.session_state.username = username
                st.session_state.authentication_status = authentication_status
                st.session_state.user_role = credentials['usernames'][username].get('role', 'customer')
                
                # Update last login time
                credentials['usernames'][username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_users(credentials)
                
                st.success("Login successful!")
                st.experimental_rerun()
                
        except Exception as e:
            st.error(f"Login error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("📝 Create Account")
        
        try:
            if authenticator.register_user('Register', preauthorization=False):
                # Add role and timestamps to new user
                new_username = list(credentials['usernames'].keys())[-1]
                credentials['usernames'][new_username]['role'] = 'customer'
                credentials['usernames'][new_username]['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                credentials['usernames'][new_username]['last_login'] = None
                
                save_users(credentials)
                st.success('User registered successfully! Please login.')
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("🔒 Reset Password")
        
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password('Forgot password')
            
            if username_of_forgotten_password:
                st.success('New password sent securely')
                # Update the user's password in credentials
                credentials['usernames'][username_of_forgotten_password]['password'] = stauth.Hasher([new_random_password]).generate()[0]
                save_users(credentials)
            elif username_of_forgotten_password == False:
                st.error('Username not found')
        except Exception as e:
            st.error(f"Password reset error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# User is authenticated - show main application
else:
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown("<div class='logout-container'>", unsafe_allow_html=True)
        user_data = credentials['usernames'][st.session_state.username]
        st.write(f"👋 Welcome, **{user_data['name']}**")
        st.write(f"🎭 Role: **{st.session_state.user_role.upper()}**")
        
        if authenticator.logout_button('Logout', 'sidebar'):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.session_state.user_role = None
            st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Navigation based on user role
        if st.session_state.user_role == 'admin':
            st.subheader("🔧 Admin Panel")
            if st.button("User Management"):
                st.session_state.current_page = "user_management"
            if st.button("View Analytics"):
                st.session_state.current_page = "analytics"
        
        # Common navigation
        st.subheader("🛍️ Shopping")
        if st.button("Browse Products"):
            st.session_state.current_page = "products"
        if st.button("Order History"):
            st.session_state.current_page = "orders"
        if st.button("Account Settings"):
            st.session_state.current_page = "settings"

    # Main content area
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "products"
    
    # Admin-only pages
    if st.session_state.user_role == 'admin':
        if st.session_state.current_page == "user_management":
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.title("👥 User Management")
            
            for username, user_data in credentials['usernames'].items():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{user_data['name']}** ({username})")
                with col2:
                    st.write(f"Role: {user_data.get('role', 'customer')}")
                with col3:
                    if st.button("Edit", key=f"edit_{username}"):
                        st.session_state.editing_user = username
            
            if 'editing_user' in st.session_state:
                user_to_edit = st.session_state.editing_user
                st.subheader(f"Editing: {user_to_edit}")
                
                new_role = st.selectbox(
                    "Role",
                    ["admin", "customer"],
                    index=0 if credentials['usernames'][user_to_edit].get('role') == 'admin' else 1
                )
                
                if st.button("Save Changes"):
                    credentials['usernames'][user_to_edit]['role'] = new_role
                    save_users(credentials)
                    del st.session_state.editing_user
                    st.success("User updated successfully!")
                    st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        elif st.session_state.current_page == "analytics":
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.title("📊 Analytics Dashboard")
            
            total_users = len(credentials['usernames'])
            admin_count = sum(1 for user in credentials['usernames'].values() if user.get('role') == 'admin')
            customer_count = total_users - admin_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", total_users)
            with col2:
                st.metric("Admins", admin_count)
            with col3:
                st.metric("Customers", customer_count)
            
            # Show recent activity
            st.subheader("Recent Activity")
            for username, user_data in list(credentials['usernames'].items())[-5:]:
                st.write(f"**{user_data['name']}** - Last login: {user_data.get('last_login', 'Never')}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # User settings page (available to all)
    if st.session_state.current_page == "settings":
        st.markdown("<div class='user-panel'>", unsafe_allow_html=True)
        st.title("⚙️ Account Settings")
        
        try:
            if authenticator.reset_password(st.session_state.username, 'Reset password'):
                save_users(credentials)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(f"Password reset error: {str(e)}")
        
        # Update user profile
        user_data = credentials['usernames'][st.session_state.username]
        new_name = st.text_input("Full Name", value=user_data['name'])
        new_email = st.text_input("Email", value=user_data['email'])
        
        if st.button("Update Profile"):
            credentials['usernames'][st.session_state.username]['name'] = new_name
            credentials['usernames'][st.session_state.username]['email'] = new_email
            save_users(credentials)
            st.success("Profile updated successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main shopping page (default)
    else:
        st.title("🛒 Welcome to Petrosini Global Investment")
        
        # Role-based welcome message
        if st.session_state.user_role == 'admin':
            st.success("👑 Administrator Mode: You have access to all features")
        else:
            st.info("🛍️ Customer Mode: Browse and shop our products")
        
        # -------------------
        # Category Selection
        # -------------------
        category = st.radio("Select a category", ["Clothes", "Generators", "Electronics"])

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
        
        elif category == "Electronics":
            st.subheader("📱 Electronics")
            st.image("https://i.imgur.com/abc123.jpg", width=200, caption="Latest Gadgets")
            if st.button("Buy Smartphone (₦80,000)"):
                st.markdown(
                    """
                    <a href="https://paystack.shop/pay/electronics123" target="_blank">
                        <button style="background-color:purple;color:white;padding:10px 20px;font-size:16px;">Pay with Paystack 💳</button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

# Create users.yaml file if it doesn't exist
if not st.session_state.get('authentication_status'):
    # Ensure the file exists
    load_users()
