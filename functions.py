import openai
from pydub import AudioSegment
import os
import config
import time
import json
from flask_babel import _

def border_25MB(media):
    """
    Check if the uploaded audio file is less than 25MB or not.
    """

    size_in_bytes = os.path.getsize(media) # get the size of audio file
    size_in_mb = size_in_bytes / (1024 * 1024)  # convert bytes to MB

    if size_in_mb < 25:
        return True
    else:
        return False



def transcribe(media, text, language):
    """
    Call Whisper API for transcribing uploaded file.
    This can be used solely if the file is smaller than 25MB.
    In case if it is larger than 25MB, another function dedined as "consequtive_transcribe", where this is embedded in it, will be called.
    """

    # setup the Whisper API configuration
    API_key = config.gpt_api_key
    model_id = "whisper-1"
    media_path = media
    media_file = open(media_path, "rb")

    # prompt differs in language of uploaded file
    if language == "Japanese":
        prompt_text = f"""
    このオーディオファイルの音声は日本語です。 \n
    内容は、記者が録音した記者会見やインタビューです。\n 
    下記のルールに従って、文字起こしをして下さい。:\n
    
    まず、文字起こしには必ず句読点を入れて読みやすくして下さい。例えば次のような形です: \"こんにちは。そうですね、わかりました。ありがとうございます。\"\n\n
    
    次に、相槌や思考中に呟く言葉なども含めて文字起こしをして下さい。例えば次のようになります: \"うーん、まあえっと、そうですね、やはり、そうしましょう.\"\n\n
    
    最後に、文字起こしは次のテキストに自然に続くようにして下さい。: \n\n{text} 
    """
        print(f"Prompt is {prompt_text}")
        
    else:
        prompt_text = f"""
    The audio file is in English. \n
    In many cases, the contents are press conferences and interviews that journalists have recorded.\n
    Please transcribe it in accordance with the following rules:
    
    Firstly, always include all punctuation, such as periods and commas, in the transcript. An example response might look like this: \"Hello, welcome to my lecture.\"\n\n
    
    Secondly, do not omit common filler words or interjections that appear in the audio. For instance, if the audio contains phrases like \"Umm, let me think like, hmm... Okay, here's what I'm, like, thinking.\", they should be included in the transcript.\n\n
    
    Lastly, ensure the transcription of this audio file is coherent with the following previous part: \n\n{text} 
    """
        print(f"Prompt is {prompt_text}")

    # Call Whisper API
    response = openai.Audio.transcribe(
        api_key = API_key,
        model = model_id,
        file = media_file,
        prompt = prompt_text
    )
    return response["text"]



def consective_transcribe(media, language):
    """
    This should be used if the file is larger than 25MB.
    This function separate the file into several pieces so that each piece has less than 25MB.
    After transcribing each separated file respectively, texts are concatenated as single transcription.  
    """

    # setup the variables to split audio file
    media_path = media # path or file name
    media_title = media_path.split(".")[0] #split by "." and pick up path and/or title 
    media_type = media_path.split(".")[-1] #split by "." and pick up extension of the file
    audio_file = AudioSegment.from_file(media_path, format=media_type) #reads the uploaded audio file into an AudioSegment object
    output_prefix = f"{media_title}_part" #set up a prefix for the names of the separated files

    one_second = 1000 #pydub works with milliseconds
    one_minute = 60 * 1000
    twenty_minutes = one_minute * 20

    total_duration_seconds = round(audio_file.duration_seconds + 1) # entire duration of audio file
    total_duration_milliseconds = total_duration_seconds * 1000 # express total duration in milliseconds

    chunk_unit = twenty_minutes # set up the duration of a separated file as 20 minutes
    chunk_titles = [] # list of all separated titles
    entire_transcription = [] # list of transcriptions for all separated files
    text = "" # this links to the parameter of the function "transcribe(media, text, language)"

    # loop over the separated files and transcribe each part 
    for indx, audio_segment in enumerate(range(0, total_duration_milliseconds, chunk_unit)):

        chunk_title = output_prefix + str(indx+1) + "." + media_type # generate separated file's title
        chunk_titles.append(chunk_title) 

        # export separated files to the "uploads" folder and save them as designated title
        audio_file[audio_segment:audio_segment + twenty_minutes].export(chunk_title, format=media_type)

        # Call Whsper API
        part_response = transcribe(chunk_title, text, language)
        print(f"{chunk_title} has been transcribed as follows: {part_response}")

        # from the second time of the loop, text will be the previous part of transcription so that the entire transcription flows smoothly
        text = part_response

        entire_transcription.append(part_response)
        os.remove(chunk_title) # delate separated files from "uploads"
        print(f"Deleted file: {chunk_title}")

    # concatenate all the transcriptions and return it
    answer = "".join(entire_transcription)
    print(f"The file was separated into {len(chunk_titles)} sub-files. They are titled as follows: {chunk_titles}")
    return answer
    

def process(media, language):
    """function to handle the entire process"""

    media = str(media)
    
    # Start the timer
    start_time = time.time()
    
    if border_25MB(media):
        print(f"{media} is NOT larger than 25MB.")

        # read uploaded file
        media_path = media
        media_type = media_path.split(".")[-1] #pick up extensions
        audio_file = AudioSegment.from_file(media_path, format=media_type)

        # caluculate the duration of the uploaded file 
        duration_seconds = round(audio_file.duration_seconds, 0)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = _("録音時間：&nbsp;&nbsp;{hours:02}:{minutes:02}:{seconds:02}").format(hours=int(hours), minutes=int(minutes), seconds=int(seconds))

        # transcribe with Whisper API
        transcription = transcribe(media, "", language).replace('"', '')
        transcription = _("実行結果：<br>{transcription}").format(transcription=transcription)
        
        # End the timer and calculate the runtime
        end_time = time.time()
        runtime = round(end_time - start_time, 1)
        runhours, remained = divmod(runtime, 3600)
        runmin, runsec = divmod(remained, 60)
        runtime = _("実行時間：&nbsp;&nbsp;{runhours:02}:{runmin:02}:{runsec:02}").format(runhours=int(runhours), runmin=int(runmin), runsec=int(runsec))

        # return the formatted output
        outcome = "<br>".join([duration_formatted, runtime, transcription])
        print(f"The result is as follows: {outcome}")

        return outcome

    else:
        print(f"{media} is larger than 25MB.")

        media_path = media
        media_type = media_path.split(".")[-1] 
        audio_file = AudioSegment.from_file(media_path, format=media_type)

        duration_seconds = round(audio_file.duration_seconds, 0)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = _("録音時間：&nbsp;&nbsp;{hours:02}:{minutes:02}:{seconds:02}").format(hours=int(hours), minutes=int(minutes), seconds=int(seconds))

        transcription = consective_transcribe(media, language).replace('"', '')
        transcription = _("実行結果：<br>{transcription}").format(transcription=transcription)
        
        end_time = time.time()
        runtime = round(end_time - start_time, 1)
        runhours, remained = divmod(runtime, 3600)
        runmin, runsec = divmod(remained, 60)
        runtime = _("実行時間：&nbsp;&nbsp;{runhours:02}:{runmin:02}:{runsec:02}").format(runhours=int(runhours), runmin=int(runmin), runsec=int(runsec))

        outcome = "<br>".join([duration_formatted, runtime, transcription])
        print(f"The result is as follows: {outcome}")
        
        return outcome
