import os
import json
from typing import Dict, List, Any
from scripts.data.helpers import download_audio, get_transcript
from scripts.data.diarization import create_diarization_pipeline, diarize_audio

# R1 | META | LOC:BEACH | SPY:P3 | ROLES:P1:SUNBATHER,P2:LIFEGUARD,P3:SPY,P4:VENDOR
# R1 | P1 | ASK | P2 | What's the temperature like here?
# R1 | P2 | ANSWER | P1 | It's quite comfortable, neither hot nor cold.
# R1 | P2 | ASK | P3 | How long have you been working here?
# R1 | P3 | ANSWER | P2 | Oh, I've been around for a while now.
# R<round_number> | P<player_number> | <action> | T<target_player> | <dialogue>

diarization_pipeline = create_diarization_pipeline()

def extract_info(audio_path: str, transcript: str) -> Dict:
    # TODO: preprocess audio and transcript
    # preprocessed_audio = preprocess_audio(audio_path)
    # preprocessed_transcript = preprocess_transcript(transcript)

    speaker_segments = speaker_diarization(audio_path)

    rounds = segment_rounds(speaker_segments)
    analyzed_rounds = []
    for round_num, round_data in enumerate(rounds, 1):
        round_metadata = extract_round_metadata(round_data)
        round_actions = extract_round_actions(round_data)
        analyzed_rounds.append({
            "metadata": round_metadata,
            "actions": round_actions
        })

    return format_output(analyzed_rounds)

def preprocess_audio(audio_path: str) -> Any:

    pass

def preprocess_transcript(transcript: str) -> str:
    return transcript

def speaker_diarization(audio_path: str) -> List[Dict]:
    results = diarize_audio(diarization_pipeline, audio_path)
    return results

def segment_rounds(speaker_segments: List[Dict]) -> List[List[Dict]]:
    pass

def extract_round_metadata(round_data: List[Dict]) -> Dict:
    pass

def extract_round_actions(round_data: List[Dict]) -> List[Dict]:
    pass

def format_output(analyzed_rounds: List[Dict]) -> str:
    formatted_lines = []
    for round_num, round_data in enumerate(analyzed_rounds, 1):
        metadata = round_data["metadata"]
        formatted_lines.append(f"R{round_num} | META | LOC:{metadata['location']} | SPY:{metadata['spy']} | ROLES:{','.join(f'{p}:{r}' for p, r in metadata['roles'].items())}")
        
        for action in round_data["actions"]:
            formatted_lines.append(f"R{round_num} | {action['player']} | {action['type']} | {action['target']} | {action['dialogue']}")
    
    return "\n".join(formatted_lines)

def process_video(video_url, output_dir):
    video_id = video_url.split("v=")[-1]
    audio_path = os.path.join(output_dir, video_id, "audio")
    
    download_audio(video_url, audio_path)
    transcript = get_transcript(video_id)
    
    # Save audio and transcript together
    data = {
        "audio_path": audio_path,
        "transcript": transcript
    }
    with open(os.path.join(output_dir, video_id, "data.json"), 'w') as f:
        json.dump(data, f, indent=2)

    if transcript:
        result = extract_info(audio_path + ".mp3", transcript)
        
        with open(os.path.join(output_dir, video_id, "result.json"), 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(f"Skipping extraction for video {video_id} due to missing transcript")
    
def main():
    video_urls = [
        "https://www.youtube.com/watch?v=MZbZa-14ae8"
    ]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    for url in video_urls:
        process_video(url, output_dir)

if __name__ == "__main__":
    main()