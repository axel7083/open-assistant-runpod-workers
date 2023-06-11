from pyngrok import ngrok
from urllib.parse import urlparse
from runpod_client import RunpodClient
import argparse
import logging
from time import sleep
from secrets import token_urlsafe
from tqdm import tqdm
from time import sleep
import requests

logging.basicConfig()
logger = logging.getLogger('runpod-worker')
logger.setLevel(logging.INFO)


class AssistantLoop:

    def __int__(self, runpod: RunpodClient, vs_code_url: str):
        self.runpod = runpod
        self.vs_code_url = vs_code_url

    def loop(self):
        pass



def program_loop(runpod: RunpodClient, vs_code_url: str):
    # Get the initial balance
    balance, rate = runpod.get_balance()

    # Set the initial total_fmt to the first balance value
    total_fmt = balance

    # Define the tqdm progress bar format
    bar_format = "{l_bar}{bar}| start={total_fmt}€ [{elapsed}{postfix}€]"

    is_vs_up = requests.get(vs_code_url).status_code == 200

    # Create a tqdm progress bar
    with tqdm(total=balance, bar_format=bar_format) as pbar:
        while balance > 0:
            # Update the progress bar description
            pbar.set_postfix(balance=balance, rate=rate, code_server_running=is_vs_up)

            # Calculate the incremental progress based on the current balance
            new_balance, new_rate = runpod.get_balance()
            increment = balance - new_balance

            # Update the progress bar
            pbar.update(increment)

            # Update the balance
            balance -= increment
            rate = new_rate

            # Update total_fmt if balance is greater than the initial value
            if balance > total_fmt:
                total_fmt = balance

            # Change the color if the balance is below 1
            if balance < 1:
                pbar.bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}] |{bar}| [RED]"

            is_vs_up = requests.get(vs_code_url).status_code == 200

            sleep(10)


def clear(runpod: RunpodClient, pod_id: str, ngrok_process):
    print("Killing ngrok..")
    ngrok.kill()
    print("Killing runpod..")
    runpod.terminate_pod(pod_id)
    print("Everything cleared.")


def main(api_key: str):
    runpod = RunpodClient(api_key=api_key)

    # Creating wss tunnel
    ssh_tunnel = ngrok.connect(8000)
    logger.info(f"Created tunnel: {ssh_tunnel}")
    ngrok_process = ngrok.get_ngrok_process()

    password = token_urlsafe(12)
    parsed = urlparse(ssh_tunnel.public_url)
    pod_id = runpod.create_pod(
        container_disk_in_gb=100,
        gpu_type_id="NVIDIA A100 80GB PCIe",
        image_name="docker.io/axel7083/oasst-inference-worker:v1-code-server-1686477536",
        ports='8888/http',
        env={
            "BACKEND_URL": f'wss://{parsed.hostname}',
            # "MODEL_CONFIG_NAME": "OA_SFT_Pythia_12Bq_4",
            "MODEL_ID": "elinas/llama-30b-hf-transformers-4.29",
            "PASSWORD": password
        }
    )

    logger.info(f"Pod created: {pod_id}. Password: {password}")

    try:
        built_url = f"https://{pod_id}-8888.proxy.runpod.net/"
        logger.info(f'Accessing pod at {built_url}')
        logger.warning('The server will probably gonna take some time to boot.')
        # Block until CTRL-C or some other terminating event
        program_loop(runpod, built_url)
    except KeyboardInterrupt:
        clear(runpod, pod_id, ngrok_process)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key", required=True)

    args = parser.parse_args()
    main(args.api_key)