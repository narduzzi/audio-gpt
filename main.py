import os
from pathlib import Path
from openai import OpenAI
import playsound
import soundfile as sf
import time
import sounddevice as sd
import numpy as np

client = OpenAI()
tmp_working_dir = Path(__file__).parent / "tmp"
if not os.path.exists(tmp_working_dir):
    os.makedirs(tmp_working_dir)

speech_recording_filepath = os.path.join(tmp_working_dir, "recording.wav")
text2speech_filepath = os.path.join(tmp_working_dir, "speech.wav")


def record_audio_with_silence_threshold(threshold=0.02, silence_duration=1.0, fs=44100):
    """
    Record audio until there is a silence of specified duration.

    :param threshold: The threshold to consider as silence.
    :param silence_duration: The duration of silence in seconds to stop recording.
    :param fs: Sampling frequency.
    :return: Recorded audio data.
    """

    # Parameters
    samplerate = fs  # Sample rate in Hertz
    channels = 1  # Mono recording
    filename = speech_recording_filepath

    # Initialize buffer and flags
    audio_buffer = []
    recording = True
    last_loud_time = time.time()

    def audio_callback(indata, time, status):
        if status:
            print(status)
        audio_buffer.append(indata.copy())
        if np.max(np.abs(indata)) > threshold:
            last_loud_time = time.inputBufferAdcTime

    # Create and start the stream
    with sd.InputStream(callback=audio_callback, channels=channels, samplerate=samplerate):
        print("Recording started...")

        while recording:
            if (time.time() - last_loud_time) > silence_duration:
                recording = False
            time.sleep(0.1)

    # Concatenate all the buffered audio chunks
    recorded_audio = np.concatenate(audio_buffer, axis=0)

    # Save the recorded data as a WAV file
    sf.write(filename, recorded_audio, samplerate)
    print(f"Recording saved as {filename}")
    return filename


def get_assistant(name):
    assistants = client.beta.assistants.list()
    assistant = None
    for a in assistants:
        if a.name == name:
            assistant = a
            break

    if assistant is None:
        # create assistant with name 'name'
        assistant = client.beta.assistants.create(
            name=name,
            description="Assistant for the project"
        )

    return assistant


def get_assistant_response(request_message, thread, assistant):
    # post message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=request_message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    while run_status.status != "completed":
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        time.sleep(0.1)
    print("Jarvis: ", end="")
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    for thread_message in messages.data[:1]:
        if thread_message.role == "assistant":
            reply = thread_message.content[-1].text.value
            return reply


def generate_audio_from_text(text, speed=1.0):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        speed=speed
    )

    response.stream_to_file(text2speech_filepath)

    return text2speech_filepath


def play_response():
    print("Playing response")
    playsound.playsound(text2speech_filepath, True)


if __name__ == '__main__':
    assistant = get_assistant("Jarvis")
    if "THREAD_ID" in os.environ:
        thread_id = os.environ["THREAD_ID"]
    else:
        thread = client.beta.threads.create()
        thread_id = thread.id

    thread = client.beta.threads.retrieve(thread_id=thread_id)

    while True:
        print("YOU: ", end="")
        my_input = input()
        use_audio = False

        if my_input == "r":
            print("Start recording...")
            filename = record_audio_with_silence_threshold(threshold=0.02, silence_duration=3.0)
            print("Audio file saved.")

            audio_file = open(filename, "rb")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            my_input = transcript.text
            use_audio = True

        if my_input == "exit":
            break

        if len(my_input) >= 2:
            reply = get_assistant_response(my_input, thread,
                                           assistant=assistant)  # get reply in this thread by assistant
            print(reply)
            if use_audio:
                sound_file = generate_audio_from_text(reply, speed=1.1)
                print("Playing response")
                playsound.playsound(sound_file, True)

    print("Quit")
