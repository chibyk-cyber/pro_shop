import streamlit as st
import pandas as pd
from api import *

# Page configuration
st.set_page_config(
    page_title="Pro Shop Management System",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Authentication functions
def login():
    st.title("🔐 Login")
    
    users = get_users()
    credentials = {'usernames': {}}
    
    for username, password, name, role in users:
        credentials['usernames'][username] = {
            'name': name,
            'password': password
        }
    
    try:
        authenticator = stauth.Authenticate(
            credentials,
            'pro_shop_cookie',
            'pro_shop_key',
            cookie_expiry_days=1
        )
        
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        if authentication_status:
            st.session_state.authenticated = True
            st.session_state.current_user = username
            # Get user role from database
            for user in users:
                if user[0] == username:
                    st.session_state.user_role = user[3]
                    break
            st.rerun()
        elif authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')
            
    except Exception as e:
        st.error(f"Authentication error: {e}")

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.rerun()

# Main application
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.current_user}!")
    st.sidebar.write(f"Role: {st.session_state.user_role}")
    
    if st.sidebar.button("🚪 Logout"):
        logout()
    
    # Navigation based on user role
    if st.session_state.user_role == 'admin':
        menu_options = ["Dashboard", "Product Management", "Sales", "User Management", "Reports"]
    else:
        menu_options = ["Dashboard", "Product Management", "Sales"]
    
    selected_menu = st.sidebar.selectbox("Navigation", menu_options)
    
    if selected_menu == "Dashboard":
        show_dashboard()
    elif selected_menu == "Product Management":
        manage_products()
    elif selected_menu == "Sales":
        process_sales()
    elif selected_menu == "User Management" and st.session_state.user_role == 'admin':
        manage_users()
    elif selected_menu == "Reports" and st.session_state.user_role == 'admin':
        show_reports()

def show_dashboard():
    st.title("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    products = get_products()
    total_products = len(products)
    total_stock = products['stock'].sum()
    total_value = (products['price'] * products['stock']).sum()
    
    with col1:
        st.metric("Total Products", total_products)
    with col2:
        st.metric("Total Stock", total_stock)
    with col3:
        st.metric("Inventory Value", f"${total_value:,.2f}")
    
    st.subheader("Low Stock Alert")
    low_stock = products[products['stock'] < 10]
    if not low_stock.empty:
        st.dataframe(low_stock[['name', 'category', 'stock']])
    else:
        st.success("All products have sufficient stock!")

def manage_products():
    st.title("📦 Product Management")
    
    tab1, tab2, tab3 = st.tabs(["View Products", "Add Product", "Edit Product"])
    
    with tab1:
        products = get_products()
        st.dataframe(products)
    
    with tab2:
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            category = st.selectbox("Category", ["Electronics", "Clothing", "Books", "Sports", "Other"])
            price = st.number_input("Price", min_value=0.0, step=0.01)
            stock = st.number_input("Stock", min_value=0, step=1)
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Product"):
                if name and category and price >= 0 and stock >= 0:
                    add_product(name, category, price, stock, description)
                    st.success("Product added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all fields correctly!")
    
    with tab3:
        products = get_products()
        if not products.empty:
            product_to_edit = st.selectbox("Select Product to Edit", 
                                         products['name'].tolist(),
                                         key='edit_select')
            
            product_data = products[products['name'] == product_to_edit].iloc[0]
            
            with st.form("edit_product_form"):
                new_name = st.text_input("Product Name", value=product_data['name'])
                new_category = st.selectbox("Category", 
                                          ["Electronics", "Clothing", "Books", "Sports", "Other"],
                                          index=["Electronics", "Clothing", "Books", "Sports", "Other"].index(product_data['category']))
                new_price = st.number_input("Price", value=float(product_data['price']), min_value=0.0, step=0.01)
                new_stock = st.number_input("Stock", value=int(product_data['stock']), min_value=0, step=1)
                new_description = st.text_area("Description", value=product_data['description'] if pd.notna(product_data['description']) else "")
                
                if st.form_submit_button("Update Product"):
                    update_product(product_data['id'], new_name, new_category, new_price, new_stock, new_description)
                    st.success("Product updated successfully!")
                    st.rerun()
        else:
            st.info("No products available to edit.")

def process_sales():
    st.title("💰 Process Sales")
    
    products = get_products()
    if products.empty:
        st.warning("No products available for sale.")
        return
    
    selected_product = st.selectbox("Select Product", products['name'].tolist())
    product_data = products[products['name'] == selected_product].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Price:** ${product_data['price']:.2f}")
        st.write(f"**Available Stock:** {product_data['stock']}")
    
    with col2:
        quantity = st.number_input("Quantity", min_value=1, max_value=product_data['stock'], value=1)
        total_price = quantity * product_data['price']
        st.write(f"**Total:** ${total_price:.2f}")
    
    if st.button("Process Sale", type="primary"):
        if quantity <= product_data['stock']:
            # Record sale
            record_sale(product_data['id'], quantity, total_price)
            # Update stock
            new_stock = product_data['stock'] - quantity
            update_product(product_data['id'], product_data['name'], product_data['category'], 
                          product_data['price'], new_stock, product_data['description'])
            st.success(f"Sale processed successfully! Total: ${total_price:.2f}")
            st.rerun()
        else:
            st.error("Not enough stock available!")

def manage_users():
    if st.session_state.user_role != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("👥 User Management")
    
    users = get_users()
    st.subheader("Current Users")
    user_df = pd.DataFrame(users, columns=['Username', 'Password', 'Name', 'Role'])
    st.dataframe(user_df[['Username', 'Name', 'Role']])
    
    st.subheader("Add New User")
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_name = st.text_input("Full Name")
        with col2:
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "staff"])
        
        if st.form_submit_button("Add User"):
            if new_username and new_password and new_name:
                if add_user(new_username, new_password, new_name, new_role):
                    st.success("User added successfully!")
                    st.rerun()
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please fill all fields!")

def show_reports():
    if st.session_state.user_role != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("📈 Reports")
    
    sales_data = get_sales_report()
    
    if not sales_data.empty:
        st.subheader("Sales History")
        st.dataframe(sales_data)
        
        # Sales summary
        total_sales = sales_data['total_price'].sum()
        total_quantity = sales_data['quantity'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sales Amount", f"${total_sales:,.2f}")
        with col2:
            st.metric("Total Items Sold", total_quantity)
    else:
        st.info("No sales data available.")

# Main application flow
def main():
    if not st.session_state.authenticated:
        login()
    else:
        main_app()

if __name__ == "__main__":
    main()
