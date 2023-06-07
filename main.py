from pyngrok import ngrok
from urllib.parse import urlparse
from runpod_client import RunpodClient
import argparse
import logging
from time import sleep

logging.basicConfig()
logger = logging.getLogger('runpod-worker')
logger.setLevel(logging.INFO)


def extract_connection_info(runpod: RunpodClient, pod_id: str):
    retries = 10 * 6 * 5  # 5 minutes
    while retries > 0:
        retries = retries - 1
        pods = runpod.query_pods()

        for pod in pods:
            if pod.id != pod_id:
                continue

            if pod.ports is None:
                logger.info('ports None')
                continue

            for port in pod.ports:
                if port.get('isIpPublic') == True and port.get('privatePort', 22):
                    return port.get('ip'), port.get('publicPort')

            logger.warning(f'Cannot find ssh port: {pod.ports}.')
        sleep(10)

    raise Exception('Timeout')


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

    parsed = urlparse(ssh_tunnel.public_url)
    pod_id = runpod.create_pod(
        image_name="docker.io/axel7083/oasst-inference-worker:v1-pycharm-remote-1686166474",
        ports='22/tcp',
        env={
            "BACKEND_URL": f'wss://{parsed.hostname}',
            "MODEL_CONFIG_NAME": "OA_SFT_Pythia_12Bq_4"
        }
    )

    logger.info(f"Pod created: {pod_id}")

    try:
        ip, port = extract_connection_info(runpod, pod_id)
        logger.info(f'Pod available at {ip}:{port}')
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        clear(runpod, pod_id, ngrok_process)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key", required=True)

    args = parser.parse_args()
    main(args.api_key)