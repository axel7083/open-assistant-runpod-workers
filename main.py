from pyngrok import ngrok
from urllib.parse import urlparse
from runpod_client import RunpodClient
import argparse
import logging
from time import sleep
from secrets import token_urlsafe


logging.basicConfig()
logger = logging.getLogger('runpod-worker')
logger.setLevel(logging.INFO)


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
        image_name="docker.io/axel7083/oasst-inference-worker:v1-code-server-1686249990",
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
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        clear(runpod, pod_id, ngrok_process)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key", required=True)

    args = parser.parse_args()
    main(args.api_key)