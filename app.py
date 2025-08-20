import streamlit as st
import webbrowser

st.set_page_config(page_title="My Store", page_icon="🛍️", layout="centered")

st.title("🛍️ Welcome to My Store")
st.write("Buy your **Generators** and **Clothes** here with Paystack 🚀")

# Product catalog
products = {
    "Generator": {"price": 50000, "desc": "Durable generator for your home."},
    "T-Shirt": {"price": 5000, "desc": "Comfortable cotton t-shirt."},
    "Jacket": {"price": 15000, "desc": "Stylish jacket for all weather."}
}

# Display products
for name, details in products.items():
    with st.container():
        st.subheader(f"{name} - ₦{details['price']}")
        st.write(details["desc"])
        if st.button(f"Buy {name}", key=name):
            # Paystack checkout link (use your Paystack dashboard to generate one)
            paystack_url = f"https://paystack.com/pay/your-paystack-link"
            webbrowser.open_new_tab(paystack_url)
            st.success(f"Redirecting to Paystack for {name} purchase...")

st.markdown("---")
st.info("Payments are processed securely via Paystack ✅")
