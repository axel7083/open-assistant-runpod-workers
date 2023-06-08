from pyngrok import ngrok
from urllib.parse import urlparse
from runpod_client import RunpodClient
import argparse
import logging
from time import sleep
from secrets import token_urlsafe
from tqdm import tqdm
from time import sleep


logging.basicConfig()
logger = logging.getLogger('runpod-worker')
logger.setLevel(logging.INFO)


def show_balance(runpod: RunpodClient):
    # Get the initial balance
    balance = runpod.get_balance()

    # Set the initial total_fmt to the first balance value
    total_fmt = balance

    # Define the tqdm progress bar format
    bar_format = "{l_bar}{bar}| start={total_fmt}€ [{elapsed}{postfix}€]"

    # Create a tqdm progress bar
    with tqdm(total=balance, bar_format=bar_format) as pbar:
        while balance > 0:
            # Update the progress bar description
            pbar.set_postfix(balance=balance)

            # Calculate the incremental progress based on the current balance
            new_balance = runpod.get_balance()
            increment = balance - new_balance

            # Update the progress bar
            pbar.update(increment)

            # Update the balance
            balance -= increment

            # Update total_fmt if balance is greater than the initial value
            if balance > total_fmt:
                total_fmt = balance

            # Change the color if the balance is below 1
            if balance < 1:
                pbar.bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}] |{bar}| [RED]"

            sleep(1)


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
        image_name="docker.io/axel7083/oasst-inference-worker:v1-code-server-1686253804",
        ports='8888/http',
        env={
            "BACKEND_URL": f'wss://{parsed.hostname}',
            "MODEL_CONFIG_NAME": "OA_SFT_Pythia_12Bq_4",
            "PASSWORD": password
        }
    )

    logger.info(f"Pod created: {pod_id}. Password: {password}")

    try:
        logger.info(f'Accessing pod at https://{pod_id}-8888.proxy.runpod.net/')
        logger.warning('The server will probably gonna take some time to boot.')
        # Block until CTRL-C or some other terminating event
        show_balance(runpod)
    except KeyboardInterrupt:
        clear(runpod, pod_id, ngrok_process)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key", required=True)

    args = parser.parse_args()
    main(args.api_key)