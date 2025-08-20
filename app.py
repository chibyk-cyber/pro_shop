# Firebase + Streamlit Store (Paystack, Auth, Profiles) — Full Starter Kit

This starter gives you everything you asked for:

* **Streamlit store app (Python)**

  * User **sign up / log in** with **Firebase Auth (email & password)**
  * Store & edit **user profiles** (name, phone, address) in **Firebase Realtime Database**
  * Simple **catalog + cart + checkout**
  * **Paystack** server-side **transaction initialize** → auto-redirect to Paystack checkout
  * Optional **payment verification** by reference and order saving
* **Firebase Hosting** front page with Paystack buttons + link to the Streamlit store
* **Secure Realtime Database rules** (users only access their own data)

> Replace the placeholders like `YOUR_*` with your real values.

---

## Project structure

```
my-shop/
  ├─ firebase.json
  ├─ database.rules.json
  ├─ public/
  │   └─ index.html
  └─ streamlit_app/
      ├─ app.py
      ├─ requirements.txt
      └─ .streamlit/
          └─ secrets.toml   # for Streamlit Cloud (or use env vars locally)
```

---

## 1) Firebase Hosting config — `firebase.json`

```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ]
  },
  "database": {
    "rules": "database.rules.json"
  }
}
```

---

## 2) Realtime Database rules — `database.rules.json`

```json
{
  "rules": {
    ".read": false,
    ".write": false,
    "users": {
      "$uid": {
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid"
      }
    },
    "orders": {
      "$uid": {
        ".read": "auth != null && auth.uid === $uid",
        ".write": "auth != null && auth.uid === $uid"
      }
    }
  }
}
```

> In Firebase Console, make sure you created a **Realtime Database** (not only Firestore) and set location, then deploy these rules with `firebase deploy`.

---

## 3) Firebase Hosting page — `public/index.html`

A simple landing page with Paystack quick-buy buttons and a link to your Streamlit store.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My Shop - Generators & Clothes</title>
  <script src="https://js.paystack.co/v1/inline.js"></script>
  <style>
    body { font-family: Arial, sans-serif; background:#0f1115; color:#fff; text-align:center; padding:32px; }
    .grid { display:flex; flex-wrap:wrap; gap:16px; justify-content:center; }
    .card { background:#161a22; border-radius:16px; padding:20px; width:260px; box-shadow:0 8px 24px rgba(0,0,0,.35); }
    .price { opacity:.9; margin:8px 0 16px; }
    button { border:0; border-radius:10px; padding:10px 16px; cursor:pointer; }
    .buy { background:#22c55e; color:#fff; }
    .buy:hover { filter:brightness(.95); }
    .link-btn { background:#3b82f6; color:#fff; margin-top:28px; }
  </style>
</head>
<body>
  <h1>🚀 Welcome to My Shop</h1>
  <p>Pay securely with Paystack or visit our full store.</p>

  <div class="grid">
    <div class="card">
      <h2>Generator</h2>
      <p class="price">₦50,000</p>
      <button class="buy" onclick="payWithPaystack(50000, 'generator@example.com')">Buy Now</button>
    </div>
    <div class="card">
      <h2>T‑Shirt</h2>
      <p class="price">₦5,000</p>
      <button class="buy" onclick="payWithPaystack(5000, 'tshirt@example.com')">Buy Now</button>
    </div>
  </div>

  <a href="https://YOUR-STREAMLIT-APP-URL" target="_blank">
    <button class="link-btn">Open Full Streamlit Store</button>
  </a>

  <script>
    function payWithPaystack(amountNaira, email){
      var handler = PaystackPop.setup({
        key: 'YOUR_PAYSTACK_PUBLIC_KEY', // replace
        email: email,
        amount: amountNaira * 100, // kobo
        currency: 'NGN',
        ref: '' + Math.floor((Math.random() * 1000000000) + 1),
        callback: function(response){
          alert('Payment complete! Ref: ' + response.reference);
        },
        onClose: function(){ alert('Transaction was not completed.'); }
      });
      handler.openIframe();
    }
  </script>
</body>
</html>
```

---

## 4) Streamlit app — `streamlit_app/app.py`

Fully integrated Auth + Profiles + Catalog + Cart + Paystack initialize + optional verify.

```python
import os
import json
import time
import requests
import streamlit as st
from typing import Dict, Any

# ----- SETTINGS -----
st.set_page_config(page_title="My Store", page_icon="🛍️", layout="centered")

# Load secrets / env
PAYSTACK_SECRET_KEY = st.secrets.get("PAYSTACK_SECRET_KEY", os.getenv("PAYSTACK_SECRET_KEY", ""))
FIREBASE_CONFIG_RAW = st.secrets.get("FIREBASE_CONFIG_JSON", os.getenv("FIREBASE_CONFIG_JSON", ""))

if not FIREBASE_CONFIG_RAW:
    st.warning("⚠️ Add FIREBASE_CONFIG_JSON & PAYSTACK_SECRET_KEY to .streamlit/secrets.toml or env vars.")

firebase_config: Dict[str, Any] = {}
if FIREBASE_CONFIG_RAW:
    try:
        firebase_config = json.loads(FIREBASE_CONFIG_RAW)
    except Exception as e:
        st.error(f"Invalid FIREBASE_CONFIG_JSON: {e}")

# Lazy import pyrebase to avoid crash before config
if firebase_config:
    import pyrebase
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
    db = firebase.database()
else:
    auth = None
    db = None

# ----- UI HELPERS -----
@st.cache_data
def get_catalog():
    return {
        "Generator": {"price": 50000, "desc": "Durable 2.5KVA home generator."},
        "T‑Shirt": {"price": 5000, "desc": "100% cotton tee."},
        "Jacket": {"price": 15000, "desc": "Lightweight, all‑weather jacket."}
    }

CATALOG = get_catalog()

if "user" not in st.session_state:
    st.session_state.user = None  # will store {uid, email, idToken}
if "cart" not in st.session_state:
    st.session_state.cart = {}  # name -> qty

# ----- AUTH -----
with st.sidebar:
    st.header("🔐 Account")
    mode = st.radio("Auth mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    colA, colB = st.columns(2)
    if colA.button("Submit") and auth:
        try:
            if mode == "Sign Up":
                user = auth.create_user_with_email_and_password(email, password)
                auth.send_email_verification(user["idToken"])
                st.success("Account created! Please verify your email. Logging you in...")
            user = auth.sign_in_with_email_and_password(email, password)
            info = auth.get_account_info(user["idToken"])  # optional check
            st.session_state.user = {
                "uid": info["users"][0]["localId"],
                "email": email,
                "idToken": user["idToken"],
                "refreshToken": user["refreshToken"]
            }
            st.rerun()
        except Exception as e:
            st.error(f"Auth error: {e}")
    if colB.button("Logout"):
        st.session_state.user = None
        st.session_state.cart = {}
        st.success("Logged out.")
        st.rerun()

# ----- PROFILE -----
st.title("🛍️ My Store")
if st.session_state.user and db:
    uid = st.session_state.user["uid"]
    st.subheader("👤 Profile")
    # Load existing
    snap = db.child("users").child(uid).get()
    existing = snap.val() or {}
    name = st.text_input("Full name", value=existing.get("name", ""))
    phone = st.text_input("Phone", value=existing.get("phone", ""))
    address = st.text_area("Address", value=existing.get("address", ""))
    if st.button("Save Profile"):
        try:
            db.child("users").child(uid).set({
                "name": name,
                "phone": phone,
                "address": address,
                "email": st.session_state.user["email"],
                "updatedAt": int(time.time())
            })
            st.success("Profile saved ✅")
        except Exception as e:
            st.error(f"Save failed: {e}")
else:
    st.info("Log in to edit your profile and checkout.")

# ----- CATALOG & CART -----
st.subheader("🛒 Products")
for item, details in CATALOG.items():
    with st.container(border=True):
        st.write(f"**{item}** — ₦{details['price']}")
        st.caption(details["desc"])
        qty = st.number_input(f"Qty — {item}", min_value=0, step=1, key=f"qty_{item}")
        if st.button(f"Add {item}", key=f"add_{item}"):
            if qty > 0:
                st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty
                st.success(f"Added {qty} × {item}")
            else:
                st.warning("Choose a quantity > 0")

st.markdown("---")

# Cart summary
if st.session_state.cart:
    st.subheader("🧾 Cart")
    total = 0
    for item, qty in st.session_state.cart.items():
        price = CATALOG[item]["price"]
        st.write(f"{qty} × {item} — ₦{price * qty}")
        total += price * qty
    st.write(f"**Total: ₦{total}**")

    # ----- CHECKOUT (Paystack initialize) -----
    if st.session_state.user and PAYSTACK_SECRET_KEY:
        email_for_payment = st.session_state.user["email"]
        if st.button("Proceed to Paystack Checkout"):
            try:
                init_payload = {
                    "email": email_for_payment,
                    "amount": total * 100,  # kobo
                    "currency": "NGN",
                    "metadata": {
                        "uid": st.session_state.user["uid"],
                        "cart": st.session_state.cart
                    }
                }
                headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
                resp = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=init_payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()["data"]
                    auth_url = data["authorization_url"]
                    reference = data["reference"]
                    st.session_state["last_ref"] = reference
                    st.success("Opening Paystack checkout...")
                    st.markdown(f"[Click here if not redirected automatically]({auth_url})", unsafe_allow_html=True)
                    st.write("If the link doesn't open, copy and paste it into a new tab:")
                    st.code(auth_url)
                else:
                    st.error(f"Paystack init failed: {resp.text}")
            except Exception as e:
                st.error(f"Error initializing payment: {e}")
    else:
        st.info("Login first and ensure PAYSTACK_SECRET_KEY is set to checkout.")
else:
    st.info("Your cart is empty. Add some products above.")

st.markdown("---")

# ----- OPTIONAL: Verify Payment by Reference & Save Order -----
st.subheader("✅ Verify Payment (optional)")
ref = st.text_input("Enter Paystack reference", value=st.session_state.get("last_ref", ""))
if st.button("Verify Payment") and ref and PAYSTACK_SECRET_KEY and db and st.session_state.user:
    try:
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        verify = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers, timeout=20)
        if verify.status_code == 200:
            v = verify.json()["data"]
            status = v["status"]
            amount = v["amount"] // 100
            uid = st.session_state.user["uid"]
            order = {
                "ref": ref,
                "status": status,
                "amount": amount,
                "cart": st.session_state.cart,
                "paidAt": v.get("paid_at"),
                "createdAt": int(time.time())
            }
            db.child("orders").child(uid).push(order)
            st.success(f"Payment status: {status}. Order saved.")
            if status == "success":
                st.session_state.cart = {}
        else:
            st.error(f"Verify failed: {verify.text}")
    except Exception as e:
        st.error(f"Verify error: {e}")
```

---

## 5) Streamlit dependencies — `streamlit_app/requirements.txt`

```
streamlit
pyrebase4
requests
```

> If you run locally and prefer environment variables instead of secrets, also `python-dotenv` and load them at startup.

---

## 6) Streamlit secrets — `streamlit_app/.streamlit/secrets.toml`

Fill with your real keys. On Streamlit Cloud, add the same keys in **App → Settings → Secrets**.

```toml
# Paystack backend secret (starts with sk_) — keep private!
PAYSTACK_SECRET_KEY = "sk_live_or_test_xxx"

# Put your Firebase web config JSON here as a single string
# Copy it from Firebase Console → Project settings → General → Your apps (Web) → SDK setup and config (Config)
# Example structure shown below; keep it as ONE LINE JSON in quotes
FIREBASE_CONFIG_JSON = "{\
  \"apiKey\": \"YOUR_API_KEY\", \
  \"authDomain\": \"YOUR_PROJECT_ID.firebaseapp.com\", \
  \"databaseURL\": \"https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com\", \
  \"projectId\": \"YOUR_PROJECT_ID\", \
  \"storageBucket\": \"YOUR_PROJECT_ID.appspot.com\", \
  \"messagingSenderId\": \"YOUR_SENDER_ID\", \
  \"appId\": \"YOUR_APP_ID\" \
}"
```

> **Important:** Enable **Email/Password** in **Firebase Authentication → Sign-in method**. Create a **Realtime Database** and note the **databaseURL**.

---

## 7) Commands to run & deploy

### Install Firebase CLI (once)

```bash
npm install -g firebase-tools
firebase login
```

### Initialize & deploy Hosting

```bash
cd my-shop
firebase init hosting   # select existing project, public = public
firebase deploy
```

### Run Streamlit locally

```bash
cd streamlit_app
pip install -r requirements.txt
# set envs if not using secrets.toml
# export PAYSTACK_SECRET_KEY=sk_test_xxx
# export FIREBASE_CONFIG_JSON='{"apiKey":"...","databaseURL":"..."}'
streamlit run app.py
```

### Deploy Streamlit to Streamlit Cloud

* Push `streamlit_app/` to GitHub.
* On Streamlit Cloud: **New app** → pick repo → `streamlit_app/app.py`.
* Add **Secrets** using the `secrets.toml` values above.
* After it gives you the URL, replace `YOUR-STREAMLIT-APP-URL` in `public/index.html`.

---

## Notes & best practices

* **Never expose** your `PAYSTACK_SECRET_KEY` in the frontend (HTML). It should only live in Streamlit secrets or server env.
* Use the **Verify** section (or a webhook on your own server) to confirm payments before delivering items.
* You can extend profiles with avatar, delivery prefs, etc. They’re saved at `/users/{uid}`; orders at `/orders/{uid}`.
* If you prefer **Firestore** instead of Realtime DB, switch to `firebase_admin` SDK in Python and use Firestore client; rules would be different.

That’s it — you now have Hosting, Auth, Profiles, Cart, and Paystack wired together. Replace the placeholders and deploy! 🚀
