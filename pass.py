import streamlit_authenticator as stauth

passwords = ['abc123', 'def456']
hasher = stauth.Hasher(passwords)
hashed_passwords = hasher.generate()
print(hashed_passwords)
