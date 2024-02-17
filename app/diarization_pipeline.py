import torch
from pyannote.audio import Pipeline

from .diarize import (
    post_process_segments_and_transcripts,
    diarize_audio,
    preprocess_inputs,
)


def diarize(hf_token, file_name, outputs):
    diarization_pipeline = Pipeline.from_pretrained(
        checkpoint_path="pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token,
    )
    diarization_pipeline.to(torch.device("cuda:0"))

    inputs, diarizer_inputs = preprocess_inputs(inputs=file_name)

    segments = diarize_audio(diarizer_inputs, diarization_pipeline)
    return post_process_segments_and_transcripts(
        segments, outputs["chunks"], group_by_speaker=False
    )
