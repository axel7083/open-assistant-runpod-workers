Redacted the 06/06/2023 _(probably outdated the day you will read this.)_

# open-assistant-runpod-workers
 
In the [Open-Assistant](https://github.com/LAION-AI/Open-Assistant) project, in the docker-compose the inference workers is deployed locally, if you do not have a powerfull GPU, this make it useless.

The script in this repository allows to spawn a worker in [runpod.io](https://www.runpod.io/) a cloud provider allowing you to rent a GPU for almost nothing.

## Requirements

- You will need an api key from your runpod account (and some money on it. Like 5 euros is enough for testing a few hours).
- ngrok installed on your machine


### ngrok

ngork allows to make the bridge between your local development dockers and the workers in the runpod cloud.

## Usage

````shell
pip install -r requirements.txt
python main.py --api-key={api-key}
````
