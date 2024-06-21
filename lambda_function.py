import json
import openai
import requests

def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'])

def on_launch(request):
    return build_response("Welcome to the GLaDOS Assistant. How can I help you today?")

def on_intent(request):
    intent_name = request['intent']['name']
    if intent_name == "GLaDOSIntent":
        user_command = request['intent']['slots']['Command']['value']
        response_text = glados_response(user_command)
        speech_url = generate_glados_voice(response_text)
        return build_audio_response(response_text, speech_url)
    elif intent_name in ("AMAZON.HelpIntent", "AMAZON.CancelIntent", "AMAZON.StopIntent"):
        return build_response("Goodbye.")
    else:
        raise ValueError("Invalid intent")

def on_session_ended(request):
    return build_response("Session ended.")

def build_response(output_text):
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output_text
            },
            'shouldEndSession': True
        }
    }

def build_audio_response(output_text, speech_url):
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': f'<speak><audio src="{speech_url}"/></speak>'
            },
            'shouldEndSession': True
        }
    }

def glados_response(command):
    openai.api_key = 'your_openai_api_key'
    prompt = f"""
    You are GLaDOS, the AI from the Portal video game series. You are known for your dark humor, sarcasm, and condescending attitude. Respond to the following user command in your unique style, staying true to your personality:

    User: {command}
    GLaDOS:
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.9
    )
    return response.choices[0].text.strip()

def generate_glados_voice(text):
    elevenlabs_api_key = 'your_elevenlabs_api_key'
    response = requests.post(
        'https://api.elevenlabs.io/v1/text-to-speech',
        headers={
            'Authorization': f'Bearer {elevenlabs_api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'text': text,
            'voice': 'glados'
        }
    )
    response_data = response.json()
    return response_data['audio_url']
