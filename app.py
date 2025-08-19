import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
import re

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
# Load/Save User Data - FIXED
# -------------------
def load_users():
    try:
        with open('users.yaml', 'r') as file:
            data = yaml.load(file, Loader=SafeLoader)
            if data is None:
                # Create default users if file is empty
                return create_default_users()
            return data
    except FileNotFoundError:
        return create_default_users()

def create_default_users():
    # Create default users with properly hashed passwords
    default_users = {
        'usernames': {
            'admin': {
                'email': 'admin@petrosini.com',
                'name': 'System Administrator',
                'password': stauth.Hasher(['1234']).generate()[0],  # Fixed: generate hash properly
                'role': 'admin',
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_login': None
            },
            'customer': {
                'email': 'customer@example.com',
                'name': 'Valued Customer',
                'password': stauth.Hasher(['abcd']).generate()[0],  # Fixed: generate hash properly
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
        yaml.dump(users, file, default_flow_style=False)

# Load users
credentials = load_users()

# Create authenticator object - FIXED parameter order
authenticator = stauth.Authenticate(
    credentials,  # Fixed: pass the credentials directly
    'petrosini_auth',
    'petrosini_auth_key',
    cookie_expiry_days=7
)

# -------------------
# Authentication Flow - FIXED
# -------------------
# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "products"

# Main app logic
if not st.session_state.get('authentication_status'):
    # Show login/register tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔒 Forgot Password"])
    
    with tab1:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("🔑 Login to Shop")
        
        try:
            # Fixed: Use the correct authentication flow
            username, authentication_status, _ = authenticator.login('Login', 'main')
            
            if authentication_status:
                st.session_state.username = username
                st.session_state.authentication_status = authentication_status
                st.session_state.user_role = credentials['usernames'][username].get('role', 'customer')
                
                # Update last login time
                credentials['usernames'][username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_users(credentials)
                
                st.success("Login successful!")
                st.experimental_rerun()
            elif authentication_status is False:
                st.error("Invalid username or password")
                
        except Exception as e:
            st.error(f"Login error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("📝 Create Account")
        
        try:
            # Fixed: Simplified registration process
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Register"):
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    elif new_username in credentials['usernames']:
                        st.error("Username already exists!")
                    else:
                        # Create new user
                        credentials['usernames'][new_username] = {
                            'email': new_email,
                            'name': new_name,
                            'password': stauth.Hasher([new_password]).generate()[0],
                            'role': 'customer',
                            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'last_login': None
                        }
                        save_users(credentials)
                        st.success('User registered successfully! Please login.')
                        
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.title("🔒 Reset Password")
        
        try:
            # Fixed: Simplified password reset
            reset_username = st.text_input("Enter your username")
            if st.button("Reset Password"):
                if reset_username in credentials['usernames']:
                    # Generate a simple reset code (in real app, send via email)
                    reset_code = "123456"  # Simplified for demo
                    st.info(f"Your reset code is: {reset_code}")
                    st.info("In a real application, this would be sent to your email.")
                else:
                    st.error("Username not found")
                    
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
        
        if st.button("Logout"):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.current_page = "products"
            st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Navigation based on user role
        if st.session_state.user_role == 'admin':
            st.subheader("🔧 Admin Panel")
            if st.button("User Management", key="user_mgmt"):
                st.session_state.current_page = "user_management"
            if st.button("View Analytics", key="analytics"):
                st.session_state.current_page = "analytics"
        
        # Common navigation
        st.subheader("🛍️ Shopping")
        if st.button("Browse Products", key="products"):
            st.session_state.current_page = "products"
        if st.button("Order History", key="orders"):
            st.session_state.current_page = "orders"
        if st.button("Account Settings", key="settings"):
            st.session_state.current_page = "settings"

    # Main content area
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
                    index=0 if credentials['usernames'][user_to_edit].get('role') == 'admin' else 1,
                    key=f"role_{user_to_edit}"
                )
                
                if st.button("Save Changes", key=f"save_{user_to_edit}"):
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
            st.subheader("Recent Users")
            for username, user_data in list(credentials['usernames'].items())[-5:]:
                st.write(f"**{user_data['name']}** - Created: {user_data.get('created_at', 'Unknown')}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # User settings page (available to all)
    if st.session_state.current_page == "settings":
        st.markdown("<div class='user-panel'>", unsafe_allow_html=True)
        st.title("⚙️ Account Settings")
        
        user_data = credentials['usernames'][st.session_state.username]
        new_name = st.text_input("Full Name", value=user_data['name'], key="name_input")
        new_email = st.text_input("Email", value=user_data['email'], key="email_input")
        
        # Simple password reset form
        st.subheader("Change Password")
        current_pw = st.text_input("Current Password", type="password", key="current_pw")
        new_pw = st.text_input("New Password", type="password", key="new_pw")
        confirm_pw = st.text_input("Confirm New Password", type="password", key="confirm_pw")
        
        if st.button("Update Profile", key="update_profile"):
            if new_pw and new_pw != confirm_pw:
                st.error("New passwords don't match!")
            else:
                credentials['usernames'][st.session_state.username]['name'] = new_name
                credentials['usernames'][st.session_state.username]['email'] = new_email
                if new_pw:  # Only update password if provided
                    credentials['usernames'][st.session_state.username]['password'] = stauth.Hasher([new_pw]).generate()[0]
                save_users(credentials)
                st.success("Profile updated successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif st.session_state.current_page == "orders":
        st.markdown("<div class='user-panel'>", unsafe_allow_html=True)
        st.title("📋 Order History")
        st.info("Your order history will appear here once you make purchases.")
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
            st.image("https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400", width=200)
            if st.button("Buy T-Shirt (₦10,000)", key="tshirt_btn"):
                st.markdown(
                    """
                    <a href="https://paystack.shop/pay/af5ijd14sl" target="_blank">
                        <button style="background-color:green;color:white;padding:10px 20px;font-size:16px;border-radius:8px;">Pay with Paystack 💳</button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

        elif category == "Generators":
            st.subheader("⚡ Generators")
            st.image("https://images.unsplash.com/photo-1580619305218-8427a47d35f0?w=400", width=200)
            if st.button("Buy Generator (₦150,000)", key="generator_btn"):
                st.markdown(
                    """
                    <a href="https://paystack.shop/pay/83og7ge8mt" target="_blank">
                        <button style="background-color:blue;color:white;padding:10px 20px;font-size:16px;border-radius:8px;">Pay with Paystack 💳</button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
        
        elif category == "Electronics":
            st.subheader("📱 Electronics")
            st.image("https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=400", width=200)
            st.write("Latest smartphones and gadgets")
            if st.button("Buy Smartphone (₦80,000)", key="phone_btn"):
                st.markdown(
                    """
                    <a href="https://paystack.shop/pay/electronics123" target="_blank">
                        <button style="background-color:purple;color:white;padding:10px 20px;font-size:16px;border-radius:8px;">Pay with Paystack 💳</button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
