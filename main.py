# Import required libraries
import asyncio
from EdgeGPT import Chatbot, ConversationStyle
import re
import whisper
import pydub
from pydub import playback
import speech_recognition as sr
from gtts import gTTS
import os

# Create a recognizer object and wake word variable
recognizer = sr.Recognizer()
WAKE_WORD = "hello"


def get_wake_word(phrase):
    if WAKE_WORD in phrase.lower():  
        # Check if wake word is present in the recognized phrase
        return WAKE_WORD
    else:
        return None


def synthesize_speech(text, output_filename):
    tts = gTTS(text=text, lang='en')  
    # Generate speech using gTTS library
    tts.save(output_filename)


def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")  
    # Load audio file
    playback.play(sound)  
    # Play the audio


async def main():
    while True:

        with sr.Microphone() as source:  
            # Set microphone as audio source
            recognizer.adjust_for_ambient_noise(source)  
            # Adjust recognizer for ambient noise
            print(f"Waiting for wake word '{WAKE_WORD}'...")
            while True:
                audio = recognizer.listen(source)  
                # Listen to microphone input
                try:
                    with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())  
                        # Save the audio data to a file
                    model = whisper.load_model("tiny")  
                    # Load the whisper model
                    result = model.transcribe("audio.wav")  
                    # Transcribe the audio using the model
                    phrase = result["text"]  
                    # Get the transcribed text
                    print(f"You said: {phrase}")

                    wake_word = get_wake_word(phrase)  
                    # Check if wake word is present
                    if wake_word is not None:
                        break  
                        # Exit the loop if wake word is detected
                    else:
                        print("Not a wake word. Try again.")
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue

            print("Speak a prompt...")
            synthesize_speech('What can I help you with?', 'response.mp3')  
            # Generate and save prompt speech
            play_audio('response.mp3')  
            # Play the prompt audio
            audio = recognizer.listen(source)  
            # Listen to user's prompt

            try:
                with open("audio_prompt.wav", "wb") as f:
                    f.write(audio.get_wav_data())  
                    # Save the prompt audio data to a file
                model = whisper.load_model("base")  
                # Load the whisper model
                result = model.transcribe("audio_prompt.wav")  
                # Transcribe the prompt audio
                user_input = result["text"]  
                # Get the transcribed text
                print(f"You said: {user_input}")
            except Exception as e:
                print("Error transcribing audio: {0}".format(e))
                continue

            if wake_word == WAKE_WORD:
                bot = Chatbot(cookie_path='/Users/aniketsethi/Documents/Coding/voiceassistant/cookies.json')  
                # Create Chatbot instance
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)  
                # Ask Chatbot for response
                # Select only the bot response from the response dictionary
                for message in response["item"]["messages"]:
                    if message["author"] == "bot":
                        bot_response = message["text"]
                # Remove [^#^] citations in response
                bot_response = re.sub('\[\^((?!\*|\d+\^).)*\]', '', bot_response)

            else:
                bot_response = "Error: Wake word not recognized"

        print("Bot's response:", bot_response)
        synthesize_speech(bot_response, 'response.mp3')  
        # Generate and save the bot's response as speech
        play_audio('response.mp3')  
        # Play the bot's response audio
        await bot.close()  
        # Close the Chatbot instance
        os.remove('response.mp3')  
        # Remove the temporary response audio file


    # Run the main function asynchronously using asyncio
if __name__ == "__main__":
    asyncio.run(main())