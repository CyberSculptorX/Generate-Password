# Add file path to .txt file around lines 94 and 263.
# Install all requirements. (pip install package_name etc...)
# python main.py to run
# press the ESC to break/stop program. (Escape Key on keyboard to close the program)
# Author CyberSX

import tkinter as tk
from tkinter import Label, Button, Entry, StringVar, Text, Scrollbar, messagebox
import os
import random
import threading
import time
import string
import secrets
from itertools import permutations

# Global variables
start_time = 0
stop_event = None
timer_running = False
permutations_list = []

# Define file path here
file_path = r"***ENTER THE FILE PATH TO THE .TXT FILE HERE ***"

# Function to generate a strong password
def generate_strong_password(length=15):
    if length < 15:
        raise ValueError("Password length should be at least 15 characters")

    alphabet = string.ascii_letters
    digits = string.digits
    punctuation = string.punctuation

    password = [
        secrets.choice(alphabet),
        secrets.choice(digits),
        secrets.choice(punctuation)
    ]

    all_characters = alphabet + digits + punctuation
    password.extend(secrets.choice(all_characters) for _ in range(length - len(password)))
    random.SystemRandom().shuffle(password)

    return ''.join(password)

def read_file_in_chunks(file_path, chunk_size=1024 * 1024):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data

def search_permutations_in_file(permutations_list, file_path, result_text_var, status_label_var, stop_event, timer_label_var):
    global start_time
    found = False
    total_size = os.path.getsize(file_path)
    processed_size = 0

    start_time = time.time()

    for data in read_file_in_chunks(file_path):
        if stop_event.is_set():
            status_label_var.config(text="Search stopped by user", fg="yellow")
            return found

        lines = data.splitlines()
        for line_number, line in enumerate(lines, start=1):
            processed_size += len(line)
            line = line.strip()
            for perm in permutations_list:
                if perm == line:
                    found = True
                    result_text_var.set(f"Password found in line {line_number}: {line}")
                    status_label_var.config(text="Password found!", fg="red", font=('Arial', 18, 'bold'))
                    elapsed_time = time.time() - start_time
                    timer_label_var.set(format_time(elapsed_time))
                    stop_event.set()
                    global timer_running
                    timer_running = False
                    return found

    if not found:
        result_text_var.set("Password not found")
        status_label_var.config(text="This password is not in the text file.", fg="green", font=('Arial', 18, 'bold'))
        elapsed_time = time.time() - start_time
        timer_label_var.set(format_time(elapsed_time))
        timer_running = False
    return found

def format_time(elapsed_time):
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    return f"Elapsed Time: {hours}h {minutes}m {seconds}s"

def fetch_random_lines():
    random_lines_text.delete('1.0', tk.END)
    total_size = os.path.getsize(file_path)
    random_position = random.randint(0, total_size)
    lines = []
    chunk_size = 1024 * 1024

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        file.seek(random_position)
        data = file.read(chunk_size)
        lines.extend(data.splitlines())

    random_lines = random.sample(lines, min(1000, len(lines)))
    random_lines_text.insert(tk.END, "Random Lines:\n\n")
    for line in random_lines:
        random_lines_text.insert(tk.END, f"{line}\n")

def copy_to_clipboard():
    content = random_lines_text.get('1.0', tk.END)
    root.clipboard_clear()
    root.clipboard_append(content)

def clear_input_and_reset():
    entry.delete(0, 'end')
    random_lines_text.delete('1.0', tk.END)
    result_text.set("")
    status_label.config(text="")
    timer_label_var.set("")
    global timer_running
    timer_running = False

def update_canvas_color():
    global permutations_list
    user_input = entry.get()
    permutations_list = generate_permutations(user_input)

    try:
        global stop_event
        stop_event = threading.Event()
        global timer_running
        timer_running = True

        timer_thread = threading.Thread(target=search_with_timer, args=(permutations_list, file_path, result_text, status_label, stop_event, timer_label_var))
        timer_thread.start()

    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text="Error occurred", fg="red")

def search_with_timer(permutations_list, file_path, result_text_var, status_label_var, stop_event, timer_label_var):
    found = search_permutations_in_file(permutations_list, file_path, result_text_var, status_label_var, stop_event, timer_label_var)
    stop_timer()

def update_timer_label():
    global start_time
    while timer_running:
        elapsed_time = time.time() - start_time
        timer_label_var.set(format_time(elapsed_time))
        time.sleep(1)

def stop_scanning():
    global stop_event
    stop_event.set()
    status_label.config(text="Search stopped by user", fg="yellow", font=('Arial', 18, 'bold'))

def stop_timer():
    global timer_running
    timer_running = False

def start_password_checking():
    global permutations_list
    user_input = entry.get()
    permutations_list = generate_permutations(user_input)
    status_label.config(text="Scan started. Please wait...", fg="yellow", font=('Arial', 18, 'bold'))
    update_canvas_color()

def generate_permutations(input_text):
    words = input_text.split()
    return [''.join(perm) for perm in permutations(words)]

def open_password_length_window():
    password_length_window = tk.Toplevel(root)
    password_length_window.title("Password Length")

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    password_length_window.geometry(f"{width}x{height}")
    password_length_window.configure(bg="black")

    Label(password_length_window, text="Enter length of password:", bg="black", fg="green", font=('Arial', 18)).pack(pady=15)

    password_length_var = StringVar()
    password_length_entry = Entry(password_length_window, textvariable=password_length_var, width=20, font=('Arial', 18), justify="center")
    password_length_entry.pack(pady=10)

    def generate_password_with_length():
        try:
            length = int(password_length_var.get())
            password = generate_strong_password(length)
            entry.delete(0, tk.END)
            entry.insert(0, password)
            password_length_window.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    generate_button = Button(password_length_window, text="Generate Password", command=generate_password_with_length, bg="green", fg="black", font=('Arial', 18))
    generate_button.pack(pady=10)

def close_window(event=None):
    root.destroy()

root = tk.Tk()
root.title("Password Checker and Random Lines Viewer")
root.geometry("1000x800")
root.configure(bg="black")
root.overrideredirect(True)
root.bind('<Escape>', close_window)

# Password Generation Section
password_frame = tk.Frame(root, bg="black")
password_frame.pack(side="top", fill="both", expand=True)

button_font = ('Arial', 16)
button_width = 25

generate_button = Button(password_frame, text="Generate Password", command=open_password_length_window, bg="green", fg="black", font=button_font, width=button_width)
generate_button.pack(pady=10)

Label(password_frame, text="Enter Password Below for Checking:", bg="black", fg="green", font=('Arial', 18)).pack(pady=15)
entry = Entry(password_frame, width=60, font=('Arial', 14), justify="center")  # Centering text in Entry widget
entry.pack(pady=15)

status_label = Label(password_frame, text="", bg="black", fg="green", font=('Arial', 18))
status_label.pack(pady=15)

result_text = StringVar()
Label(password_frame, textvariable=result_text, bg="black", fg="green", wraplength=600, justify="left", font=('Arial', 14)).pack(pady=15)

timer_label_var = StringVar()
timer_label_var.set("")
timer_label = Label(password_frame, textvariable=timer_label_var, bg="black", fg="green", font=('Arial', 14))
timer_label.pack(pady=15)

# Buttons Section (Moved under password generation)
buttons_frame = tk.Frame(password_frame, bg="black")
buttons_frame.pack(pady=10)

check_button = Button(buttons_frame, text="Check Password", command=start_password_checking, bg="green", fg="black", font=button_font, width=button_width)
check_button.pack(side="left", padx=10, pady=10)

stop_button = Button(buttons_frame, text="Stop Searching", command=stop_scanning, bg="green", fg="black", font=button_font, width=button_width)
stop_button.pack(side="left", padx=10, pady=10)

fetch_button = Button(buttons_frame, text="Fetch Random Lines", command=fetch_random_lines, bg="green", fg="black", font=button_font, width=button_width)
fetch_button.pack(side="left", padx=10, pady=10)

clear_button = Button(buttons_frame, text="Clear All", command=clear_input_and_reset, bg="green", fg="black", font=button_font, width=button_width)
clear_button.pack(side="left", padx=10, pady=10)

# Random Lines Viewer Section
random_lines_frame = tk.Frame(root, bg="black")
random_lines_frame.pack(side="bottom", fill="both", expand=True)

scrollbar = Scrollbar(random_lines_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

random_lines_text = Text(random_lines_frame, wrap="word", bg="black", fg="green", yscrollcommand=scrollbar.set, font=('Arial', 14))
random_lines_text.pack(pady=15, fill="both", expand=True)
scrollbar.config(command=random_lines_text.yview)

root.state('zoomed')
root.mainloop()
