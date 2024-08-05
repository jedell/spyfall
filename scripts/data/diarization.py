import torch
from pyannote.audio import Pipeline
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

def create_diarization_pipeline() -> Pipeline:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.getenv("HF_TOKEN"))
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
    
    return pipeline

def diarize_audio(pipeline: Pipeline, audio_path: str) -> List[Dict]:
    diarization = pipeline(audio_path)
    
    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        results.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return results
