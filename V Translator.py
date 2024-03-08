import ctypes
import pyttsx3
import os
import glob
from pathlib import Path
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from datetime import timedelta
import srt
from moviepy.editor import *
from moviepy.editor import TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

ctypes.windll.kernel32.SetConsoleTitleW("V Translator")

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

def tts(message):
    
    engine.say(message)
    engine.runAndWait()

def clean():
    
    os.system("cls")

if __name__ == "__main__":
    
    videos = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "*.mp4"))

    clean()

    tts("Please choose the language into which you wish to translate your video !")
    lang = input("Please choose the language into which you wish to translate your video : ")

    clean()

    for video_path in videos:

        tts(f"Video in translation : {video_path}")
        print(f"Video in translation : {video_path}")

        model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        segments, info = model.transcribe(video_path, vad_filter=True)

        tts(f"Language spoken in the video : {info.language}")
        print(f"Language spoken in video : {info.language}")

        subtitles_data = []

        for segment in segments:

            translate = GoogleTranslator(source="auto", target=lang).translate(segment.text)
            subtitles_data.append({"start": segment.start, "end": segment.end, "text": translate})

            print(f"Original text : {segment.text}")
            print(f"Translated text : {translate}")

        subtitles = []

        for subtitle in subtitles_data:

            text = subtitle["text"]
            
            start_time = timedelta(seconds=subtitle["start"])
            end_time = timedelta(seconds=subtitle["end"])
            
            subtitles.append(srt.Subtitle(subtitle["start"], start_time, end_time, text))

        srt_file = os.path.join(os.path.dirname(video_path), Path(video_path).stem + ".srt")

        with open(srt_file, "w") as f:
            
            f.write(srt.compose(subtitles))

        generator = lambda txt: TextClip(txt, font="Arial", fontsize=32, color="black")

        subs = SubtitlesClip(srt_file, generator)
        subtitles = SubtitlesClip(subs, generator)

        video_clip = VideoFileClip(video_path)

        output_path = os.path.join(os.path.dirname(video_path), Path(video_path).stem + f"_{lang}.mp4")

        result = CompositeVideoClip([video_clip, subtitles.set_pos(("center", "bottom"))])
        result.write_videofile(output_path)

        os.remove(srt_file)
