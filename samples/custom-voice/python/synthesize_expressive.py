#!/usr/bin/env python
# coding: utf-8
# Synthesize expressive audio using SSML prosody, break, and emphasis controls.

import os
from pathlib import Path
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv(Path(__file__).resolve().parent / '.env')
region = os.environ['REGION']
key = os.environ['KEY']

SPEAKER_PROFILE_ID = '0f70d5e8-f141-491f-936d-cb6a06083a1a'
OUTPUT_DIR = Path(__file__).resolve().parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)


def synthesize(ssml_body: str, output_file: str, lang: str = 'en-US'):
    output_path = str(OUTPUT_DIR / output_file)
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
    file_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    ssml = (
        "<speak version='1.0' xml:lang='en-US' "
        "xmlns='http://www.w3.org/2001/10/synthesis' "
        "xmlns:mstts='http://www.w3.org/2001/mstts'>"
        "<voice name='DragonLatestNeural'>"
        f"<mstts:ttsembedding speakerProfileId='{SPEAKER_PROFILE_ID}'/>"
        "<mstts:express-as style='Prompt'>"
        f"<lang xml:lang='{lang}'>"
        f"{ssml_body}"
        "</lang>"
        "</mstts:express-as>"
        "</voice></speak>"
    )

    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f'OK: {output_file}')
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f'FAIL: {output_file} - {details.reason}')
        if details.reason == speechsdk.CancellationReason.Error:
            print(f'  Error: {details.error_details}')


# --- 1. English: Storytelling with rhythm and emotion ---
synthesize(
    '<prosody rate="medium" pitch="+0%">'
    'Once upon a time, <break time="300ms"/>'
    'in a land far, <emphasis level="moderate">far</emphasis> away, '
    '<break time="200ms"/>'
    'there lived a young dreamer.'
    '</prosody>'
    '<break time="500ms"/>'
    '<prosody rate="slow" pitch="-5%">'
    'He gazed at the stars every night, <break time="200ms"/>'
    'wondering if someday, <break time="300ms"/>'
    '<prosody rate="x-slow" pitch="+10%">'
    'he could touch the sky.'
    '</prosody>'
    '</prosody>'
    '<break time="600ms"/>'
    '<prosody rate="medium" pitch="+5%" volume="+10%">'
    'And one day, <break time="200ms"/>'
    '<emphasis level="strong">he did.</emphasis>'
    '</prosody>',
    'expressive_en_story.wav',
    lang='en-US'
)

# --- 2. Chinese: Poetic narration with pauses and pitch variation ---
synthesize(
    '<prosody rate="slow" pitch="+0%">'
    '春风拂过山岗，<break time="300ms"/>'
    '花儿悄悄绽放。'
    '</prosody>'
    '<break time="500ms"/>'
    '<prosody rate="medium" pitch="+5%">'
    '远方的路，<break time="200ms"/>'
    '<emphasis level="moderate">漫长而美丽</emphasis>，'
    '<break time="200ms"/>'
    '每一步都值得期待。'
    '</prosody>'
    '<break time="500ms"/>'
    '<prosody rate="slow" pitch="-5%" volume="soft">'
    '夜深了，<break time="300ms"/>'
    '星光洒满大地，'
    '<break time="200ms"/>'
    '</prosody>'
    '<prosody rate="x-slow" pitch="+10%" volume="+15%">'
    '梦想，从未远去。'
    '</prosody>',
    'expressive_cn_poem.wav',
    lang='zh-CN'
)

# --- 3. Bilingual: Energetic tech presentation style ---
synthesize(
    '<prosody rate="fast" pitch="+5%" volume="+10%">'
    'Hey everyone! <break time="200ms"/>'
    "Welcome to today's demo."
    '</prosody>'
    '<break time="400ms"/>'
    '<prosody rate="medium" pitch="+0%">'
    "We've been working on something <emphasis level=\"strong\">incredible</emphasis>."
    '<break time="300ms"/>'
    "Let me show you what AI can really do."
    '</prosody>'
    '<break time="500ms"/>'
    '<prosody rate="medium" pitch="+3%">'
    '大家好！<break time="200ms"/>'
    '今天我要给大家展示一个<emphasis level="strong">非常酷</emphasis>的技术。'
    '<break time="300ms"/>'
    '准备好了吗？'
    '</prosody>'
    '<break time="400ms"/>'
    '<prosody rate="slow" pitch="+8%" volume="+15%">'
    "Let's go!"
    '</prosody>',
    'expressive_bilingual_demo.wav',
    lang='en-US'
)

print('\nAll files saved to output/ folder.')
