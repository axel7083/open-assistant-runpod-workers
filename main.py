from pyngrok import ngrok
from urllib.parse import urlparse
from runpod_client import RunpodClient
import argparse


def main(api_key: str):
    runpod = RunpodClient(api_key=api_key)
    ssh_tunnel = ngrok.connect(8000)
    print(f"Created tunnel: {ssh_tunnel}")

    parsed = urlparse(ssh_tunnel.public_url)
    pod_id = runpod.create_pod(
        image_name="axel7083/oasst-inference-worker:v1",
        env={
            "BACKEND_URL": f'wss://{parsed.hostname}',
            "MODEL_CONFIG_NAME": "OA_SFT_Pythia_12Bq_4"
        }
    )

    print(f"Pod created: {pod_id}")
    ngrok_process = ngrok.get_ngrok_process()

    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("Killing ngrok..")
        ngrok.kill()
        print("Killing runpod..")
        runpod.terminate_pod(pod_id)
        print("Everything cleared.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="API key", required=True)

    args = parser.parse_args()
    main(args.api_key)