import os
import subprocess
import whisper
import pandas as pd
from pytube import YouTube
import streamlit as st

def shorten_audio(audio_filename):
    # Example of shortening audio, this should be adjusted based on your needs
    return audio_filename

def generate_translation(text, language):
    # Example of translation logic
    return [f"Translated text in {language}: {line}" for line in text]

def combine_video(video_filename, audio_filename):
    ffmpeg_extract_subclip(video_filename, 0, 60, targetname="cut_video.mp4")
    output_filename = "output.mp4"
    command = ["ffmpeg", "-y", "-i", "cut_video.mp4", "-i", audio_filename, "-c:v", "copy", "-c:a", "aac", output_filename]
    subprocess.run(command)
    return output_filename

st.title("AutoDubs 📺🎵")

link = st.text_input("Link to Youtube Video", key="link")

language = st.selectbox("Translate to", ("French", "German", "Hindi", "Italian", "Polish", "Portuguese", "Spanish"))

if st.button("Transcribe!"):
    print(f"downloading from link: {link}")
    model = whisper.load_model("base")
    yt = YouTube(link)

    if yt is not None:
        st.subheader(yt.title)
        st.image(yt.thumbnail_url)
        audio_name = st.caption("Downloading audio stream...")
        audio_streams = yt.streams.filter(only_audio=True)
        filename = audio_streams.first().download()
        if filename:
            audio_name.caption(filename)
            cut_audio = shorten_audio(filename)
            transcription = model.transcribe(cut_audio)
            print(transcription)
            if transcription:
                df = pd.DataFrame(transcription['segments'], columns=['start', 'end', 'text'])
                st.dataframe(df)

                dubbing_caption = st.caption("Generating translation...")

                translation = generate_translation(transcription['text'], language)

                dubbing_caption = st.caption("Begin dubbing...")
                dubs_audio = generate_dubs(translation)
                dubbing_caption.caption("Dubs generated! combining with the video...")

                video_streams = yt.streams.filter(only_video=True)
                video_filename = video_streams.first().download()

                if video_filename:
                    dubbing_caption.caption("Video downloaded! combining the video and the dubs...")
                    output_filename = combine_video(video_filename, dubs_audio)
                    if os.path.exists(output_filename):
                        dubbing_caption.caption("Video successfully dubbed! Enjoy! 😀")
                        st.video(output_filename)
