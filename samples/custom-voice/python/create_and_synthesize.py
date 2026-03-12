#!/usr/bin/env python
# coding: utf-8
# Create a personal voice using the formal API and synthesize audio with it.

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

import customvoice
import azure.cognitiveservices.speech as speechsdk

# Load config from .env
load_dotenv(Path(__file__).resolve().parent / '.env')
region = os.environ['REGION']
key = os.environ['KEY']

logging.basicConfig(filename="customvoice.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

config = customvoice.Config(key, region, logger)

# --- Configuration ---
project_id = 'joey-personal-voice-project'
consent_id = 'joey-consent'
personal_voice_id = 'joey-voice'
consent_file_path = str(Path(__file__).resolve().parent / 'consent_joey.wav')
audio_folder = str(Path(__file__).resolve().parent / 'voice_audio')
voice_talent_name = 'Joey Zeng'
company_name = 'Microsoft'


def create_personal_voice():
    # Step 1: Create project
    project = customvoice.Project.create(config, project_id, customvoice.ProjectKind.PersonalVoice)
    print(f'Project created: {project.id}')

    # Step 2: Upload consent
    consent = customvoice.Consent.create(config, project_id, consent_id,
                                         voice_talent_name, company_name,
                                         consent_file_path, 'en-us')
    if consent.status == customvoice.Status.Failed:
        print(f'Consent failed: {consent.id}')
        raise Exception('Consent creation failed')
    print(f'Consent succeeded: {consent.id}')

    # Step 3: Create personal voice
    personal_voice = customvoice.PersonalVoice.create(config, project_id,
                                                       personal_voice_id,
                                                       consent_id, audio_folder)
    if personal_voice.status == customvoice.Status.Failed:
        print(f'Personal voice failed: {personal_voice.id}')
        raise Exception('Personal voice creation failed')
    print(f'Personal voice succeeded: {personal_voice.id}')
    print(f'Speaker profile ID: {personal_voice.speaker_profile_id}')
    return personal_voice.speaker_profile_id


def synthesize(text, output_file, speaker_profile_id, lang='en-US'):
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


try:
    # Create personal voice
    speaker_profile_id = create_personal_voice()

    # Synthesize Chinese
    synthesize('今天天气真不错，我们一起去公园散步吧。',
               'output_formal_cn.wav', speaker_profile_id, lang='zh-CN')

    # Synthesize English
    synthesize('Hello, this is Joey speaking. The weather is lovely today.',
               'output_formal_en.wav', speaker_profile_id, lang='en-US')

except Exception as e:
    print(f'Error: {e}')
