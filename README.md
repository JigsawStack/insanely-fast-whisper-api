# Insanely Fast Whisper API
An API to transcribe audio with [OpenAI's Whisper Large v3](https://huggingface.co/openai/whisper-large-v3)! Powered by 🤗 Transformers, Optimum & flash-attn

Features:
* 🎤 Transcribe audio to text at blazing fast speeds
* 📖 Fully open source and deployable on any GPU cloud provider
* 🗣️ Built-in speaker diarization
* ⚡ Easy to use and Fast API layer
* 📃 Async background tasks and webhooks
* 🔥 Optimized for concurrency and parallel processing
* ✅ Task management, cancel and status endpoints
* 🔒 Admin authentication for secure API access
* 🧩 Fully managed API available on [JigsawStack](https://jigsawstack.com/speech-to-text)

Based on [Insanely Fast Whisper CLI](https://github.com/Vaibhavs10/insanely-fast-whisper) project. Check it out if you like to set up this project locally or understand the background of insanely-fast-whisper.

This project is focused on providing a deployable blazing fast whisper API with docker on cloud infrastructure with GPUs for scalable production use cases.

With [Fly.io recent GPU service launch](https://fly.io/docs/gpus/gpu-quickstart/), I've set up the fly config file to easily deploy on fly machines! However, you can deploy this on any other VM environment that supports GPUs and docker.


Here are some benchmarks we ran on Nvidia A100 - 80GB and fly.io GPU infra👇
| Optimization type    | Time to Transcribe (150 mins of Audio) |
|------------------|------------------|
| **large-v3 (Transformers) (`fp16` + `batching [24]` + `Flash Attention 2`)** | **~2 (*1 min 38 sec*)**            |
| **large-v3 (Transformers) (`fp16` + `batching [24]` + `Flash Attention 2` + `diarization`)** | **~2 (*3 min 16 sec*)**            |
| **large-v3 (Transformers) (`fp16` + `batching [24]` + `Flash Attention 2` + `fly machine startup`)** | **~2 (*1 min 58 sec*)**            |
| **large-v3 (Transformers) (`fp16` + `batching [24]` + `Flash Attention 2` + `diarization + fly machine startup`)** | **~2 (*3 min 36 sec*)**|

The estimated startup time for the Fly machine with GPU and loading up the model is around ~20 seconds. The rest of the time is spent on the actual computation.

## Docker image
```
yoeven/insanely-fast-whisper-api:latest
```
Docker hub: [yoeven/insanely-fast-whisper-api](https://hub.docker.com/r/yoeven/insanely-fast-whisper-api)

## Deploying to Fly
- Make sure you already have access to Fly GPUs.
- Clone the project locally and open a terminal in the root
- Rename the `app` name in the `fly.toml` if you like
- Remove `image = 'yoeven/insanely-fast-whisper-api:latest'` in `fly.toml` only if you want to rebuild the image from the `Dockerfile`

[Install fly cli](https://fly.io/docs/hands-on/install-flyctl/) if don't already have it

Only need to run this the first time you launch a new fly app
```bash
fly launch
```

- Fly will prompt: `Would you like to copy its configuration to the new app? (y/N)`. Yes (`y`) to copy configuration from the repo.

- Fly will prompt: `Do you want to tweak these settings before proceeding` if you have nothing to adjust. Most of the required settings are already configured in the `fly.toml` file. No `n` to proceed and deploy.

The first time you deploy it will take some time since the image is huge. Subsequent deploys will be a lot faster.

Run the following if you want to set up speaker diarization or an auth token to secure your API:

```bash
fly secrets set ADMIN_KEY=<your_token> HF_TOKEN=<your_hf_key>
```
Run `fly secrets list` to check if the secrets exist.

To get the Hugging face token for speaker diarization you need to do the following:
1. Accept [`pyannote/segmentation-3.0`](https://hf.co/pyannote/segmentation-3.0) user conditions
2. Accept [`pyannote/speaker-diarization-3.1`](https://hf.co/pyannote/speaker-diarization-3.1) user conditions
3. Create an access token at [`hf.co/settings/tokens`](https://hf.co/settings/tokens).


Your API should look something like this:

```
https://insanely-fast-whisper-api.fly.dev
```

Run `fly logs -a insanely-fast-whisper-api` to view logs in real time of your fly machine.

## Deploying to other cloud providers
Since this is a dockerized app, you can deploy it to any cloud provider that supports docker and GPUs with a few config tweaks.

Here's an example docker command:

`docker run --name insanely-fast-whisper-api --restart=always -d --gpus all -p 9000:9000 yoeven/insanely-fast-whisper-api`

## Fully managed and scalable API 
[JigsawStack](https://jigsawstack.com) provides a bunch of powerful APIs for various use cases while keeping costs low. This project is available as a fully managed API [here](https://jigsawstack.com/speech-to-text) with enhanced cloud scalability for cost efficiency and high uptime. Sign up [here](https://jigsawstack.com) for free!


## API usage

### Authentication
If you had set up the `ADMIN_KEY` environment secret. You'll need to pass `x-admin-api-key` in the header with the value of the key you previously set.


### Endpoints
#### Base URL
If deployed on Fly, the base URL should look something like this:
```
https://{app_name}.fly.dev/{path}
```
Depending on the cloud provider you deploy to, the base URL will be different.

#### **POST** `/`
Transcribe or translate audio into text
##### Body params (JSON)
| Name    | value |
|------------------|------------------|
| url (Required) |  url of audio |
| task | `transcribe`, `translate`  default: `transcribe` |
| language | `None`, `en`, [other languages](https://huggingface.co/openai/whisper-large-v3) default: `None` Auto detects language
| batch_size | Number of parallel batches you want to compute. Reduce if you face OOMs. default: `64` |
| timestamp | `chunk`, `word`  default: `chunk` |
| diarise_audio | Diarise the audio clips by speaker. You will need to set hf_token. default:`false` |
| webhook | Webhook `POST` call on completion or error. default: `None` |
| webhook.url | URL to send the webhook |
| webhook.header | Headers to send with the webhook |
| is_async | Run task in background and sends results to webhook URL. `true`, `false` default: `false` |
| managed_task_id | Custom Task ID used to reference ongoing task. default: `uuid() v4 will be generated for each transcription task` |

#### **POST** `/upload`
Same as above, except it takes a file upload instead of a URL

#### **GET** `/tasks`
Get all active transcription tasks, both async background tasks and ongoing tasks

#### **GET** `/status/{task_id}`
Get the status of a task, completed tasks will be removed from the list which may throw an error

#### **DELETE** `/cancel/{task_id}`
Cancel async background task. Only transcription jobs created with `is_async` set to `true` can be cancelled.


## Running locally
```bash
# clone the repo
$ git clone https://github.com/jigsawstack/insanely-fast-whisper-api.git

# change the working directory
$ cd insanely-fast-whisper-api

# install torch
$ pip3 install torch torchvision torchaudio

# upgrade wheel and install required packages for FlashAttention
$ pip3 install -U wheel && pip install ninja packaging

# install FlashAttention
$ pip3 install flash-attn --no-build-isolation

# generate updated requirements.txt if you want to use other management tools (Optional)
$ poetry export --output requirements.txt

# get the path of python
$ which python3

# setup virtual environment 
$ poetry env use /full/path/to/python

# install the requirements
$ poetry install

# run the app
$ uvicorn app.app:app --reload
```

## Extra
### Shutting down fly machine programmatically
Fly machines are charged by the second and might take up to 15mins of idling before it decides to shut it self down. You can shut down the machine when you're done with the API to save costs. You can do this by sending a `POST` request to the following endpoint:
```
https://api.machines.dev/v1/apps/<app_name>/machines/<machine_id>/stop
```
Authorization header:
```
Authorization Bearer <fly_token>
```
Lear more [here](https://fly.io/docs/machines/api/machines-resource/)

## Acknowledgements

1. [Vaibhav Srivastav](https://github.com/Vaibhavs10) for writing a huge chunk of the code and the CLI version of this project.
2. [OpenAI Whisper](https://huggingface.co/openai/whisper-large-v3) 


## JigsawStack
This project is part of [JigsawStack](https://jigsawstack.com) - A suite of powerful and developer friendly APIs for various use cases while keeping costs low. Sign up [here](https://jigsawstack.com) for free!
