#!/usr/bin/env python
# coding: utf-8

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load config from .env
load_dotenv(Path(__file__).resolve().parent / '.env')
region = os.environ['REGION']
key = os.environ['KEY']

# Speaker profile ID from Speech Studio trial personal voice "Joey"
zeroshot_id = 'd18d27d1-eaa9-4b34-b815-897add8312ed'
model_url = f'https://{region}.api.cognitive.microsoft.com/customvoice/trial/zeroshots/{zeroshot_id}?api-version=2023-07-01-preview'
print(f'Using zeroshot model: {zeroshot_id}')


def synthesize_to_file(text: str, output_file_path: str, locale: str = 'en-US', base_model: str = 'DragonLatestNeural'):
    url = f'https://{region}.api.cognitive.microsoft.com/customvoice/trial/synthesis?api-version=2023-07-01-preview'
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model_url,
        'locale': locale,
        'scriptOrder': 14,
        'text': text,
        'baseModelName': base_model,
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'audio' in content_type or 'octet-stream' in content_type:
            with open(output_file_path, 'wb') as f:
                f.write(response.content)
            print(f'OK: [{text}] -> [{output_file_path}] ({len(response.content)} bytes)')
        else:
            data = response.json()
            if 'audioUrl' in data:
                audio = requests.get(data['audioUrl'])
                with open(output_file_path, 'wb') as f:
                    f.write(audio.content)
                print(f'OK: [{text}] -> [{output_file_path}] ({len(audio.content)} bytes)')
            else:
                import json as _json
                print(f'Unexpected response: {_json.dumps(data, indent=2)[:500]}')
    else:
        print(f'Error {response.status_code}: {response.text[:500]}')


# Synthesize Chinese (using predefined script index from Speech Studio)
synthesize_to_file(
    '猴子打算像渔民一样撒网。',
    'output_cn.wav',
    locale='zh-CN'
)

# Synthesize English
synthesize_to_file(
    'Hello, this is Joey speaking. The weather is lovely today.',
    'output_en.wav',
    locale='en-US'
)
