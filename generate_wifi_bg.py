import requests
import json

# Generate Wi-Fi themed 9:16 background image
url = "https://api.imagine.art/v2/imagine/image"

prompt = """
Futuristic visualization of Wi-Fi radio waves propagating through a modern home interior.
Glowing cyan and blue signal ripple patterns radiating from a Wi-Fi router.
Ethereal wave patterns spreading through rooms, bouncing off walls and furniture.
Vertical 9:16 composition optimized for mobile viewing.
Soft gradient background transitioning from deep indigo to violet.
Minimalist aesthetic with clean lines and modern design.
High detail, cinematic lighting, sci-fi atmosphere.
"""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ.get('IMAGINE_API_KEY', '')}"  # Will use env var
}

payload = {
    "prompt": prompt.strip(),
    "aspect_ratio": "9:16",
    "height": 1920,
    "width": 1080
}

print(f"Requesting image generation...")
print(f"Prompt: {prompt[:100]}...")
