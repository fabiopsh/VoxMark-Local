import requests

try:
    response = requests.post("http://127.0.0.1:8000/synthesize", json={"text": "test"})
    if response.status_code == 200 and response.headers["content-type"] == "audio/wav":
        with open("test_audio.wav", "wb") as f:
            f.write(response.content)
        print("SUCCESS: Audio received and saved.")
    else:
        print(f"FAILED: Status {response.status_code}, headers {response.headers}")
except Exception as e:
    print(f"ERROR: {e}")
