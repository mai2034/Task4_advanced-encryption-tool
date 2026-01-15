import os
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

backend = default_backend()
salt = b'secure_salt_123'  # In real apps, store salt securely


def generate_key(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(password.encode())


def encrypt_file(file_path, password):
    key = generate_key(password)
    iv = os.urandom(16)

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    with open(file_path + ".enc", 'wb') as f:
        f.write(iv + encrypted)


def decrypt_file(file_path, password):
    key = generate_key(password)

    with open(file_path, 'rb') as f:
        iv = f.read(16)
        encrypted_data = f.read()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    original_file = file_path.replace(".enc", "")
    with open(original_file, 'wb') as f:
        f.write(decrypted)


def browse_file():
    return filedialog.askopenfilename()


def encrypt_action():
    file_path = browse_file()
    password = password_entry.get()
    if file_path and password:
        encrypt_file(file_path, password)
        messagebox.showinfo("Success", "File Encrypted Successfully!")
    else:
        messagebox.showerror("Error", "Please select file and enter password")


def decrypt_action():
    file_path = browse_file()
    password = password_entry.get()
    if file_path and password:
        decrypt_file(file_path, password)
        messagebox.showinfo("Success", "File Decrypted Successfully!")
    else:
        messagebox.showerror("Error", "Please select file and enter password")


# GUI
root = tk.Tk()
root.title("Advanced Encryption Tool - AES 256")
root.geometry("400x250")

tk.Label(root, text="Advanced Encryption Tool", font=("Arial", 16)).pack(pady=10)
tk.Label(root, text="Enter Password").pack()

password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

tk.Button(root, text="Encrypt File", width=20, command=encrypt_action).pack(pady=5)
tk.Button(root, text="Decrypt File", width=20, command=decrypt_action).pack(pady=5)

root.mainloop()
