import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_art_key = os.getenv("API_ART_KEY")

def call_api_and_get_image_data(art_type):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    body = {
      "steps": 40,
      "width": 1024,
      "height": 1024,
      "seed": 0,
      "cfg_scale": 5,
      "samples": 1,
      "text_prompts": [
        {
          "text": art_type,
          "weight": 1
        },
        {
          "text": "blurry, bad",
          "weight": -1
        }
      ],
    }

    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_art_key}",
    }

    response = requests.post(
      url,
      headers=headers,
      json=body,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # Extract the base64 image data from the first artifact
    image_data = data["artifacts"][0]["base64"]

    return image_data
