Redacted the 06/06/2023 _(probably outdated the day you will read this.)_

# open-assistant-runpod-workers
 
In the [Open-Assistant](https://github.com/LAION-AI/Open-Assistant) project, in the docker-compose the inference workers is deployed locally, if you do not have a powerfull GPU, this make it useless.

The script in this repository allows to spawn a worker in [runpod.io](https://www.runpod.io/) a cloud provider allowing you to rent a GPU for almost nothing.

## Requirements

- You will need an api key from your runpod account (and some money on it. Like 5 euros is enough for testing a few hours).
- ngrok installed on your machine
- **remove the inference-worker in the docker compose.** 

### full-demo

> The following instruction are extracted from [Open-Assistant](https://github.com/LAION-AI/Open-Assistant) and [Open-Assistant/inference](https://github.com/LAION-AI/Open-Assistant/tree/main/inference)

Inside Open-Assistant repository
For the inference
````shell
docker compose --profile inference build
docker compose --profile inference up -d
docker compose logs -f inference-server
````

Then you can use the script in this repo, you will see in the docker logs of the inference-server when your worker has joined.
If nothing never appear, you can chekc the logs of your runpods

For the UI:
````shell
docker compose --profile ci up --build --attach-dependencies
````
> **Do not forget** to change the model to OA_SFT_Pythia_12Bq_4 when using the chat.

### ngrok

ngork allows to make the bridge between your local development dockers and the workers in the runpod cloud.

## Usage

````shell
pip install -r requirements.txt
python main.py --api-key={api-key}
````


## TODO:

- [ ] make the MODEL_CONFIG_NAME configurable (for now by default: `OA_SFT_Pythia_12Bq_4`)
- [ ] Make the gpu requested configurable (for now by default: `NVIDIA RTX A6000`)