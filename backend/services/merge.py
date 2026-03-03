def merge_segments(diarization_segments, transcription_segments):
    """
    Merges transcription segments (text) into diarization segments (speakers)
    based on overlapping timestamps.
    """
    merged_results = []
    
    # Simple midpoint matching strategy
    for t_seg in transcription_segments:
        t_start = t_seg["start"]
        t_end = t_seg["end"]
        t_mid = (t_start + t_end) / 2
        
        # Find the diarization segment that contains this midpoint
        assigned_speaker = "UNKNOWN"
        for d_seg in diarization_segments:
            if d_seg["start"] <= t_mid <= d_seg["end"]:
                assigned_speaker = d_seg["speaker"]
                break
                
        merged_results.append({
            "start": t_start,
            "end": t_end,
            "speaker": assigned_speaker,
            "text": t_seg["text"]
        })
        
    return merged_results
