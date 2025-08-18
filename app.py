import streamlit as st
import sqlite3

# -------------------
# Database Setup
# -------------------
def init_db():
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )''')

    # Insert default categories if not exist
    c.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (1, 'Clothes')")
    c.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (2, 'Generators')")
    conn.commit()
    conn.close()

# Initialize database
init_db()

# -------------------
# Streamlit App
# -------------------
st.set_page_config(page_title="Pro Shop", page_icon="🛒", layout="wide")
st.title("🛒 Pro Shop")

menu = st.sidebar.radio("Navigation", ["Home", "Admin Dashboard"])

if menu == "Home":
    st.subheader("Browse Products")
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    for row in c.execute("SELECT * FROM categories"):
        st.markdown(f"### {row[1]}")
        products = c.execute("SELECT name, price FROM products WHERE category_id=?", (row[0],)).fetchall()
        if products:
            for product in products:
                st.write(f"- {product[0]} — ${product[1]:.2f}")
        else:
            st.write("No products yet.")
    conn.close()

elif menu == "Admin Dashboard":
    st.subheader("Add New Product")
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    categories = c.execute("SELECT * FROM categories").fetchall()
    category_dict = {row[1]: row[0] for row in categories}

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, step=0.01)
    category = st.selectbox("Category", list(category_dict.keys()))

    if st.button("Add Product"):
        c.execute("INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)",
                  (name, price, category_dict[category]))
        conn.commit()
        st.success(f"Added {name} to {category}")
    conn.close()
