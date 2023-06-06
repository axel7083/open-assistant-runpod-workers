import json
from typing import List, Optional, Dict, Any
import requests
from models import GpuType, Pod


def _parse_gpu_types(gpu_types_data: List[dict]) -> List[GpuType]:
    gpu_types = []
    for gpu_data in gpu_types_data:
        if not gpu_data['secureCloud'] and not gpu_data['communityCloud']:
            continue

        if gpu_data['lowestPrice']['uninterruptablePrice'] == 0:
            continue

        gpu_type = GpuType(
            gpu_data['id'],
            gpu_data['displayName'],
            gpu_data['memoryInGb'],
            gpu_data['secureCloud'],
            gpu_data['communityCloud'],
            gpu_data['lowestPrice']['uninterruptablePrice']
        )
        gpu_types.append(gpu_type)
    return gpu_types


def _parse_pods(pods_data: List[dict]) -> List[Pod]:
    pods = []
    for pod_data in pods_data:

        if pod_data.get('runtime', None) is None:
            pod = Pod(
                pod_data['id'],
                pod_data['name']
            )
        else:
            pod = Pod(
                pod_data['id'],
                pod_data['name'],
                pod_data['runtime']['uptimeInSeconds'],
                pod_data['runtime']['ports'],
                pod_data['runtime']['gpus'],
                pod_data['runtime']['container']['cpuPercent'],
                pod_data['runtime']['container']['memoryPercent']
            )
        pods.append(pod)
    return pods


class RunpodClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"https://api.runpod.io/graphql?api_key={self.api_key}"

    def _send_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query, 'variables': variables}

        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")
            return None

    def query_gpu_types(self) -> List[GpuType]:
        query = """
            query GpuTypes {
                gpuTypes {
                    id
                    displayName
                    memoryInGb
                    secureCloud
                    communityCloud
                    lowestPrice(input: {gpuCount: 1}) {
                        uninterruptablePrice
                    }
                }
            }
        """

        response = self._send_request(query)
        gpu_types_data = response.get('data', {}).get('gpuTypes', [])
        return _parse_gpu_types(gpu_types_data)

    def query_pods(self) -> List[Pod]:
        query = """
            query Pods {
                myself {
                    pods {
                        id
                        name
                        runtime {
                            uptimeInSeconds
                            ports {
                                ip
                                isIpPublic
                                privatePort
                                publicPort
                                type
                            }
                            gpus {
                                id
                                gpuUtilPercent
                                memoryUtilPercent
                            }
                            container {
                                cpuPercent
                                memoryPercent
                            }
                        }
                    }
                }
            }
        """

        response = self._send_request(query)
        pods_data = response.get('data', {}).get('myself', {}).get('pods', [])
        return _parse_pods(pods_data)

    def create_pod(
        self,
        volume_in_gb: int = 40,
        container_disk_in_gb: int = 40,
        min_vcpu_count: int = 2,
        min_memory_in_gb: int = 15,
        gpu_type_id: str = "NVIDIA RTX A6000",
        name: str = "RunPod Tensorflow",
        image_name: str = "runpod/tensorflow",
        docker_args: str = "",
        ports: str = "8888/http",
        gpu_count: int = 1,
        env: Dict[str, str] = {},
        cloud_type: str = "ALL",
        volume_mount_path: str = "/workspace",
    ) -> str:
        env_str = "".join([f"{{ key: \"{key}\", value: \"{value}\"}}" for key, value in env.items()])
        mutation = f"""
            mutation {{
                podFindAndDeployOnDemand(
                    input: {{
                        cloudType: {cloud_type}
                        gpuCount: {gpu_count}
                        volumeInGb: {volume_in_gb}
                        containerDiskInGb: {container_disk_in_gb}
                        minVcpuCount: {min_vcpu_count}
                        minMemoryInGb: {min_memory_in_gb}
                        gpuTypeId: "{gpu_type_id}"
                        name: "{name}"
                        imageName: "{image_name}"
                        dockerArgs: "{docker_args}"
                        ports: "{ports}"
                        volumeMountPath: "{volume_mount_path}"
                        env: [{env_str}]
                    }}
                ) {{
                    id
                    imageName
                    env
                    machineId
                    machine {{
                        podHostId
                    }}
                }}
            }}
        """

        response = self._send_request(mutation)
        return response.get('data', {}).get('podFindAndDeployOnDemand', {}).get('id')

    def stop_pod(self, pod_id: str) -> dict:
        mutation = """
            mutation stopPod($input: PodStopInput!) {
              podStop(input: $input) {
                id
                desiredStatus
                lastStatusChange
                __typename
              }
            }
        """

        variables = {
            "input": {
                "podId": pod_id
            }
        }

        response = self._send_request(mutation, variables)
        return response.get('data', {}).get('podStop', {})

    def terminate_pod(self, pod_id: str) -> None:
        mutation = """
            mutation terminatePod($input: PodTerminateInput!) {
              podTerminate(input: $input)
            }
        """

        variables = {
            "input": {
                "podId": pod_id
            }
        }
        self._send_request(mutation, variables)