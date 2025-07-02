import streamlit as st
import pycurl
from io import BytesIO
import time
import shlex

# --- Helper Functions ---
def extract_url_from_curl(curl_cmd):
    try:
        parts = shlex.split(curl_cmd.strip())
        for part in parts:
            if part.startswith("http://") or part.startswith("https://"):
                return part
    except:
        pass
    return None

def generate_snippet(url, expected_text):
    return f'''import requests

url = "{url}"
response = requests.get(url)

if response.status_code == 200:
    print("Success! Status:", response.status_code)
    {"if \"" + expected_text + "\" in response.text: print('Expected text found')" if expected_text else ""}
else:
    print("Failed with status:", response.status_code)
'''

def run_requests(url, expected_text, iterations):
    results = []
    success_count = 0
    fail_count = 0

    for i in range(1, iterations + 1):
        if st.session_state.stop_flag:
            break

        try:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.WRITEDATA, buffer)
            c.setopt(pycurl.FOLLOWLOCATION, True)
            c.setopt(pycurl.TIMEOUT, 20)
            c.setopt(pycurl.CONNECTTIMEOUT, 10)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.SSL_VERIFYHOST, False)
            c.perform()
            status_code = c.getinfo(pycurl.RESPONSE_CODE)
            body = buffer.getvalue().decode("utf-8", errors="ignore")
            c.close()

            if expected_text in body:
                success_count += 1
                results.append((i, status_code, True))
            else:
                fail_count += 1
                results.append((i, status_code, False))
        except Exception as e:
            fail_count += 1
            results.append((i, "Error", False))

        time.sleep(0.2)

    return results, success_count, fail_count

# --- Session State Initialization ---
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

# --- UI ---
st.set_page_config(page_title="HTTP Monitor", layout="wide")
st.title("🔁 HTTP Monitor with cURL - Streamlit")

curl_cmd = st.text_area("Enter cURL Command:", "curl https://jsonplaceholder.typicode.com/posts/1", height=100)
expected_text = st.text_input("Expected Text in Response:", '"id": 1')
iterations = st.number_input("Iterations:", min_value=1, value=5)

url = extract_url_from_curl(curl_cmd)

# --- Buttons ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    run_btn = st.button("🚀 Run")
with col2:
    stop_btn = st.button("🛑 Stop")
with col3:
    show_snippet = st.button("📄 Show Code Snippet")

# --- Snippet View ---
if show_snippet and url:
    snippet = generate_snippet(url, expected_text)
    st.code(snippet, language='python')

# --- Stop Handling ---
if stop_btn:
    st.session_state.stop_flag = True
    st.warning("⛔ Execution Stopped.")

# --- Run Execution ---
if run_btn:
    if not url:
        st.error("❌ URL could not be extracted from cURL command.")
    else:
        st.session_state.stop_flag = False
        with st.spinner("Processing..."):
            results, success, fail = run_requests(url, expected_text, iterations)

        st.success(f"✅ Completed {len(results)} iterations — Success: {success}, Fail: {fail}")
        st.subheader("📋 Result Log:")
        for idx, code, status in results:
            if status:
                st.markdown(f"<span style='color:green'>Iteration [{idx}]: ✅ Successful (HTTP {code})</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:red'>Iteration [{idx}]: ❌ Failed (HTTP {code})</span>", unsafe_allow_html=True)


