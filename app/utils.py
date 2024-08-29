from PIL import Image 
import base64
import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def extract_graph_image(image_path: str):
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Find a position of graph in the image. \
                graph has few linear-dotted-lines. \
                Then, write coordinate of left-upper part and coordinate of right-lower part.\
                Write coordinate using the following template.\
                50, 50, 200, 200"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    pos = re.findall(r'\d+', response.json()['choices'][0]['message']['content'])
    pos = tuple([int(num) for num in pos[:4]])

    image = Image.open(image_path)

    cropped_image = image.crop(pos)
    cropped_image.save("../data/page-graph.png")

    return cropped_image