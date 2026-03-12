#!/usr/bin/env python
# coding: utf-8
# Synthesize audio using the formal personal voice speaker profile ID.

import os
from pathlib import Path
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv(Path(__file__).resolve().parent / '.env')
region = os.environ['REGION']
key = os.environ['KEY']

speaker_profile_id = '0f70d5e8-f141-491f-936d-cb6a06083a1a'


def synthesize(text, output_file, lang='en-US'):
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
    file_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    ssml = (
        "<speak version='1.0' xml:lang='en-US' xmlns='http://www.w3.org/2001/10/synthesis' "
        "xmlns:mstts='http://www.w3.org/2001/mstts'>"
        "<voice name='DragonLatestNeural'>"
        "<mstts:ttsembedding speakerProfileId='%s'/>"
        "<mstts:express-as style='Prompt'>"
        "<lang xml:lang='%s'> %s </lang>"
        "</mstts:express-as>"
        "</voice></speak>" % (speaker_profile_id, lang, text)
    )

    result = speech_synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f'OK: [{text}] -> [{output_file}]')
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f'Canceled: {details.reason}')
        if details.reason == speechsdk.CancellationReason.Error:
            print(f'Error: {details.error_details}')


# Synthesize Chinese
synthesize('今天天气真不错，我们一起去公园散步吧。',
           'output_formal_cn.wav', lang='zh-CN')

# Synthesize English
synthesize('Hello, this is Joey speaking. The weather is lovely today.',
           'output_formal_en.wav', lang='en-US')
