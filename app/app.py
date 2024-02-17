import os
from fastapi import FastAPI, Query, Header, HTTPException
import torch
from transformers import pipeline
from .diarization_pipeline import diarize


admin_key = os.environ.get(
    "ADMIN_KEY",
)

hf_token = os.environ.get(
    "HF_TOKEN",
)

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device="cuda:0",
    model_kwargs=({"attn_implementation": "flash_attention_2"}),
)

app = FastAPI()


@app.get("/")
def read_root(
    x_admin_api_key=Header(),
    url: str = Query(),
    task: str = Query(default="transcribe", enum=["transcribe", "translate"]),
    language: str = Query(default="None"),
    batch_size: int = Query(default=64),
    timestamp: str = Query(default="chunk", enum=["chunk", "word"]),
    diarise_audio: bool = Query(
        default=False,
    ),
):
    if admin_key is not None:
        if x_admin_api_key != admin_key:
            raise HTTPException(status_code=401, detail="Invalid API Key")

    if url.lower().startswith("http") is False:
        raise HTTPException(status_code=400, detail="Invalid URL")

    if diarise_audio is True and hf_token is None:
        raise HTTPException(status_code=500, detail="Missing Hugging Face Token")

    try:
        generate_kwargs = {
            "task": task,
            "language": None if language == "None" else language,
        }

        outputs = pipe(
            url,
            chunk_length_s=30,
            batch_size=batch_size,
            generate_kwargs=generate_kwargs,
            return_timestamps="word" if timestamp == "word" else True,
        )

        if diarise_audio is True:
            speakers_transcript = diarize(
                hf_token,
                url,
                outputs,
            )
            outputs["speakers"] = speakers_transcript

        return outputs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
