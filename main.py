import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
import subprocess
import threading
import time

# todo: Global thread and flag
stop_flag = False
execution_thread = None
success_count = 0
fail_count = 0

# todo: curL requests
def run_curl():
    global stop_flag, success_count, fail_count, execution_thread
    stop_flag = False
    curl_command = curl_input.get("1.0", tk.END).strip()
    expected_text = expected_input.get().strip()
    try:
        iterations = int(iteration_input.get())
    except ValueError:
        messagebox.showerror("Error", "Iterations must be a number.")
        return

    if not curl_command:
        messagebox.showerror("Error", "Please enter a cURL command.")
        return

    success_count = 0
    fail_count = 0

    def execute_requests():
        global success_count, fail_count
        for i in range(1, iterations + 1):
            if stop_flag:
                output.insert(tk.END, f"\nExecution stopped by user.\n")
                break
            try:
                result = subprocess.run(curl_command, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and (expected_text.lower() in result.stdout.lower() if expected_text else True):
                    success_count += 1
                    output.insert(tk.END, f"[{i}]  SUCCESS\n")
                else:
                    fail_count += 1
                    output.insert(tk.END, f"[{i}]  FAIL\n")
                output.see(tk.END)
            except subprocess.TimeoutExpired:
                fail_count += 1
                output.insert(tk.END, f"[{i}]  Timeout\n")
            except Exception as e:
                fail_count += 1
                output.insert(tk.END, f"[{i}]  Error: {e}\n")
        output.insert(tk.END, f"\n Done: Success: {success_count}, Fail: {fail_count}\n")

    execution_thread = threading.Thread(target=execute_requests)
    execution_thread.start()

# todo: Stop execution
def stop_execution():
    global stop_flag
    stop_flag = True

# todo: Clear output
def clear_output():
    output.delete(1.0, tk.END)

# todo: Generate Python snippet based on user input
def show_snippet():
    curl_cmd = curl_input.get("1.0", tk.END).strip()
    expected = expected_input.get().strip()
    iterations = iteration_input.get().strip()

    snippet_code = f'''"""
Auto-generated HTTP Request Monitor Script
"""

import requests
import time
import shlex

def parse_curl_command(curl_cmd):
    try:
        if curl_cmd.startswith('curl '):
            curl_cmd = curl_cmd[5:]

        tokens = shlex.split(curl_cmd)
        url = ""
        method = "GET"
        headers = {{}}
        data = None

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith('http'):
                url = token
            elif token in ['-X', '--request']:
                method = tokens[i + 1].upper()
                i += 1
            elif token in ['-H', '--header']:
                header_str = tokens[i + 1]
                key, value = header_str.split(':', 1)
                headers[key.strip()] = value.strip()
                i += 1
            elif token in ['-d', '--data', '--data-raw']:
                data = tokens[i + 1]
                method = "POST"
                i += 1
            i += 1

        return {{
            'url': url,
            'method': method,
            'headers': headers,
            'data': data
        }}
    except Exception as e:
        raise ValueError(f"Error parsing cURL: {{e}}")

def run_requests():
    curl_command = """{curl_cmd}"""
    expected_text = "{expected}"
    iterations = {iterations}

    config = parse_curl_command(curl_command)
    success = 0
    fail = 0

    for i in range(1, iterations + 1):
        try:
            response = requests.request(
                method=config['method'],
                url=config['url'],
                headers=config['headers'],
                data=config['data'],
                timeout=10
            )
            if response.status_code == 200 and (expected_text.lower() in response.text.lower() if expected_text else True):
                print(f"[{{i}}] SUCCESS")
                success += 1
            else:
                print(f"[{{i}}]  FAIL")
                fail += 1
        except Exception as e:
            print(f"[{{i}}]  Error: {{e}}")
            fail += 1
        time.sleep(0.1)

    print(f"\\nDone: Success={{success}}, Fail={{fail}}")

if __name__ == "__main__":
    run_requests()
'''

    # todo: Show in new window
    snippet_window = Toplevel(root)
    snippet_window.title("Auto-Generated Python Script")
    snippet_window.geometry("900x600")
    snippet_area = scrolledtext.ScrolledText(snippet_window, font=("Courier", 10), wrap="none")
    snippet_area.pack(expand=True, fill="both")
    snippet_area.insert(tk.END, snippet_code)
    snippet_area.config(state="normal")

#

root = tk.Tk()
root.title("HTTP Monitor Dashboard")
root.geometry("1000x700")
root.configure(bg="#f0f0f0")

title = tk.Label(root, text="HTTP Monitor Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="blue")
title.pack(pady=10)

curl_label = tk.Label(root, text="Enter cURL Command:", bg="#f0f0f0")
curl_label.pack()
curl_input = scrolledtext.ScrolledText(root, height=6, width=100)
curl_input.pack()

expected_label = tk.Label(root, text="Expected Text:", bg="#f0f0f0")
expected_label.pack()
expected_input = tk.Entry(root, width=50)
expected_input.pack()

iteration_label = tk.Label(root, text="Iterations:", bg="#f0f0f0")
iteration_label.pack()
iteration_input = tk.Entry(root, width=20)
iteration_input.insert(0, "5")
iteration_input.pack()

# todo: Functional Buttons Frame
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Execute", bg="green", fg="white", font=("Arial", 10, "bold"), command=run_curl).pack(side="left", padx=10)
tk.Button(btn_frame, text="Stop", bg="orange", fg="black", font=("Arial", 10, "bold"), command=stop_execution).pack(side="left", padx=10)
tk.Button(btn_frame, text="Clear", bg="red", fg="white", font=("Arial", 10, "bold"), command=clear_output).pack(side="left", padx=10)
tk.Button(btn_frame, text="Snippet", bg="purple", fg="white", font=("Arial", 10, "bold"), command=show_snippet).pack(side="left", padx=10)

# todo: Output display
output_label = tk.Label(root, text="Live Output:", bg="#f0f0f0")
output_label.pack()
output = scrolledtext.ScrolledText(root, height=20, width=120)
output.pack()

root.mainloop()
