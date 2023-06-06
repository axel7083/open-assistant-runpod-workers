from typing import List


class GpuType:
    def __init__(self, id: str, display_name: str, memory_in_gb: int, secure_cloud: bool, community_cloud: bool, lowest_price: float):
        self.id = id
        self.display_name = display_name
        self.memory_in_gb = memory_in_gb
        self.secure_cloud = secure_cloud
        self.community_cloud = community_cloud
        self.lowest_price = lowest_price

    def __str__(self):
        return f"ID: {self.id}\nDisplay Name: {self.display_name}\nMemory: {self.memory_in_gb}GB\nSecure Cloud: {self.secure_cloud}\nCommunity Cloud: {self.community_cloud}\nLowest Price: {self.lowest_price}\n"


class Pod:
    def __init__(
            self,
            id: str,
            name: str,
            uptime_in_seconds: int = None,
            ports: List[dict] = None,
            gpus: List[dict] = None,
            cpu_percent: float = None,
            memory_percent: float = None
    ):
        self.id = id
        self.name = name
        self.uptime_in_seconds = uptime_in_seconds
        self.ports = ports
        self.gpus = gpus
        self.cpu_percent = cpu_percent
        self.memory_percent = memory_percent

    def __str__(self):
        return f"ID: {self.id}\nName: {self.name}\nUptime: {self.uptime_in_seconds} seconds\nPorts: {self.ports}\nGPUs: {self.gpus}\nCPU Percent: {self.cpu_percent}\nMemory Percent: {self.memory_percent}\n"