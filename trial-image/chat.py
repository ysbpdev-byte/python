import base64
import json
import sys
import urllib.request

OLLAMA_URL = "http://192.168.2.35:11434"
MODEL = "qwen3.5"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def chat_with_image(image_path, prompt):
    print(f"Model   : {MODEL}")
    print(f"Gambar  : {image_path}")
    print(f"Prompt  : {prompt}")
    print("-" * 40)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [encode_image(image_path)]
            }
        ],
        "think": False,
        "stream": True
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print("Respons:")
    with urllib.request.urlopen(req, timeout=60) as res:
        for line in res:
            chunk = json.loads(line.decode("utf-8"))
            token = chunk.get("message", {}).get("content", "")
            print(token, end="", flush=True)
            if chunk.get("done"):
                break
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chat.py <path_to_image> [prompt]")
        print('Contoh: python chat.py foto.jpg "Apa isi gambar ini?"')
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Apa isi gambar ini? Jelaskan secara detail."

    chat_with_image(image_path, prompt)