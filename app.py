import tkinter as tk
from tkinter import ttk
import threading
import requests

# ================= CONFIG =================
OPENAI_API_KEY = "PASTE_YOUR_API_KEY_HERE"  # optional (online mode only)
OLLAMA_URL = "http://localhost:11434/api/generate"
# =========================================


def offline_ai(prompt):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return r.json().get("response", "[Offline Error] No response")
    except Exception as e:
        return f"[Offline Error] {e}"


def online_ai(prompt):
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )

        data = r.json()
        if "choices" not in data:
            return f"[Online Error] {data.get('error', data)}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[Online Error] {e}"


def process_message(user_input):
    chat.insert(tk.END, f"\nYou: {user_input}\n")
    chat.see(tk.END)

    def run_ai():
        mode = mode_var.get()
        response = offline_ai(user_input) if mode == "Offline" else online_ai(user_input)
        chat.insert(tk.END, f"AI: {response}\n")
        chat.see(tk.END)

    threading.Thread(target=run_ai, daemon=True).start()


def on_enter(event):
    # Get last line typed by user
    user_input = chat.get("end-2l linestart", "end-1c").strip()
    if not user_input:
        return "break"

    process_message(user_input)
    return "break"


# ================= UI =================
root = tk.Tk()
root.title("AI Assistant")
root.geometry("750x550")
root.configure(bg="white")

top_frame = tk.Frame(root, bg="white")
top_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Label(top_frame, text="Mode:", bg="white").pack(side=tk.LEFT)

mode_var = tk.StringVar(value="Offline")
mode_menu = ttk.Combobox(
    top_frame,
    textvariable=mode_var,
    values=["Offline", "Online"],
    state="readonly",
    width=10
)
mode_menu.pack(side=tk.LEFT, padx=5)

note = tk.Label(
    root,
    text="Note: Online mode requires a valid API key and internet connection.",
    bg="white",
    fg="gray",
    font=("Arial", 9)
)
note.pack(pady=(0, 5))

chat = tk.Text(
    root,
    bg="white",
    fg="black",
    font=("Arial", 11),
    wrap=tk.WORD
)
chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat.bind("<Return>", on_enter)

chat.insert(tk.END, "AI: Hello! Type your message and press Enter.\n")

root.mainloop()
