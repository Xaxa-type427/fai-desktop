"""FAI Desktop: minimal desktop client for an authenticated VPS inference API."""
import json
import os
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext
from urllib import request, error

BASE_URL = os.environ.get("FAI_VPS_BASE_URL", "").rstrip("/")
MODEL = os.environ.get("FAI_VPS_MODEL", "")
TOKEN = os.environ.get("FAI_VPS_API_KEY", "")

def ask(messages):
    if not BASE_URL.startswith("https://") or not MODEL:
        raise ValueError("Configure HTTPS FAI_VPS_BASE_URL and FAI_VPS_MODEL")
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    payload = json.dumps({"model": MODEL, "messages": messages, "stream": False}).encode("utf-8")
    req = request.Request(BASE_URL + "/chat/completions", data=payload, headers=headers)
    with request.urlopen(req, timeout=45) as response:
        result = json.load(response)
    return result["choices"][0]["message"]["content"]

class Desktop:
    def __init__(self, root):
        self.root = root
        root.title("FAI Desktop")
        root.geometry("740x540")
        root.configure(bg="#101923")
        self.history = [{"role": "system", "content": "You are FAI. Respond clearly in the user's language."}]
        self.events = queue.Queue()
        self.log = scrolledtext.ScrolledText(root, bg="#172633", fg="#f0f7ff", insertbackground="white", wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, padx=14, pady=14)
        row = tk.Frame(root, bg="#101923")
        row.pack(fill="x", padx=14, pady=(0, 14))
        self.input = tk.Entry(row, bg="#233a4b", fg="white", insertbackground="white")
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<Return>", lambda _: self.send())
        self.button = tk.Button(row, text="Kirim", command=self.send)
        self.button.pack(side="left", padx=(8, 0))
        self.write("Sistem", "FAI siap dibuka; koneksi VPS belum diverifikasi.")
        root.after(100, self.poll)

    def write(self, who, message):
        self.log.configure(state="normal")
        self.log.insert("end", f"{who}: {message}\n\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def send(self):
        message = self.input.get().strip()
        if not message or self.button["state"] == "disabled":
            return
        self.input.delete(0, "end")
        self.write("Kamu", message)
        self.button.configure(state="disabled")
        conversation = self.history + [{"role": "user", "content": message}]
        threading.Thread(target=self.worker, args=(conversation,), daemon=True).start()

    def worker(self, conversation):
        try:
            self.events.put(("ok", conversation, ask(conversation)))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        while not self.events.empty():
            event = self.events.get()
            if event[0] == "ok":
                _, conversation, answer = event
                self.history = conversation + [{"role": "assistant", "content": answer}]
                self.write("FAI", answer)
            else:
                self.write("Error", event[1])
            self.button.configure(state="normal")
        self.root.after(100, self.poll)

if __name__ == "__main__":
    root = tk.Tk()
    Desktop(root)
    root.mainloop()
