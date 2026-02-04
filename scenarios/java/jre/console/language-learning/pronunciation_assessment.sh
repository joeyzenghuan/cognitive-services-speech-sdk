#!/bin/bash

# Azure Speech Pronunciation Assessment - Simple cURL Script
# Usage: ./pronunciation_assessment.sh <audio_file.wav> <reference_text> [language]

# Load configuration
# 1) Source local .env if present (expects SPEECH_SUBSCRIPTION_KEY, SPEECH_REGION)
# 2) Allow overriding via environment variables SUBSCRIPTION_KEY, REGION
# 3) Fallback to placeholders if nothing provided
if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    set -a
    . ./.env
    set +a
fi

SUBSCRIPTION_KEY="${SUBSCRIPTION_KEY:-${SPEECH_SUBSCRIPTION_KEY:-YourSubscriptionKey}}"
REGION="${REGION:-${SPEECH_REGION:-westus}}"
LANGUAGE="${3:-zh-CN}"  # Default to zh-CN if not provided

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <audio_file.wav> <reference_text> [language]"
    echo "Example: $0 audio.wav \"手机号码\" zh-CN"
    exit 1
fi
# Validate key/region
if [ -z "$SUBSCRIPTION_KEY" ] || [ "$SUBSCRIPTION_KEY" = "YourSubscriptionKey" ]; then
    echo "Error: SUBSCRIPTION_KEY not set. Set SPEECH_SUBSCRIPTION_KEY in .env or export SUBSCRIPTION_KEY."
    exit 1
fi

if [ -z "$REGION" ] || [ "$REGION" = "westus" ] && [ -n "$SPEECH_REGION" ]; then
    REGION="$SPEECH_REGION"
fi

if [ -z "$REGION" ]; then
    echo "Error: REGION not set. Set SPEECH_REGION in .env or export REGION."
    exit 1
fi


AUDIO_FILE="$1"
REFERENCE_TEXT="$2"

# Check if audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file '$AUDIO_FILE' not found"
    exit 1
fi

# Build pronunciation assessment parameters JSON
PRON_PARAMS=$(cat <<EOF
{
  "GradingSystem": "HundredMark",
  "Granularity": "Phoneme",
  "Dimension": "Comprehensive",
  "ReferenceText": "$REFERENCE_TEXT",
  "EnableMiscue": true,
  "EnableProsodyAssessment": true,
  "PhonemeAlphabet": "IPA",
  "NBestPhonemeCount": 5
}
EOF
)

# Base64 encode the parameters
PRON_PARAMS_BASE64=$(echo -n "$PRON_PARAMS" | base64 -w 0)

# Generate connection ID
CONNECTION_ID=$(uuidgen | tr -d '-')

# Build URL
URL="https://${REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?format=detailed&language=${LANGUAGE}"

echo "==================================="
echo "Pronunciation Assessment Request"
echo "==================================="
echo "Audio File: $AUDIO_FILE"
echo "Reference Text: $REFERENCE_TEXT"
echo "Language: $LANGUAGE"
echo "Region: $REGION"
echo "Connection ID: $CONNECTION_ID"
echo ""
echo "Sending request..."
echo ""

# Send request
RESPONSE=$(curl -X POST "$URL" \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY" \
  -H "Content-Type: audio/wav; codecs=audio/pcm; samplerate=16000" \
  -H "Accept: application/json" \
  -H "Connection: Keep-Alive" \
  -H "Pronunciation-Assessment: $PRON_PARAMS_BASE64" \
  -H "X-ConnectionId: $CONNECTION_ID" \
  --data-binary "@$AUDIO_FILE" \
  -w "\n%{http_code}" \
  -s)

# Extract HTTP status code (last line)
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
JSON_RESPONSE=$(echo "$RESPONSE" | head -n -1)

echo "==================================="
echo "Response (HTTP $HTTP_CODE)"
echo "==================================="

if [ "$HTTP_CODE" -eq 200 ]; then
    # Pretty print JSON if jq is available
    if command -v jq &> /dev/null; then
        echo "$JSON_RESPONSE" | jq '.'
    else
        echo "$JSON_RESPONSE"
        echo ""
        echo "Tip: Install 'jq' for pretty JSON output: sudo apt-get install jq"
    fi
else
    echo "Error: Request failed with HTTP $HTTP_CODE"
    echo "$JSON_RESPONSE"
    exit 1
fi
