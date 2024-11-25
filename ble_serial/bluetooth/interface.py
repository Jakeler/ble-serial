from abc import ABC, abstractmethod

class BLE_interface(ABC):
    @abstractmethod
    def __init__(self, adapter: str, service_uuid: str, write_uuid: str, read_uuid: str):
        pass

    @abstractmethod
    def set_receiver(self, callback):
        pass

    @abstractmethod
    def queue_send(self, value: bytes):
        pass
    
    @abstractmethod
    async def send_loop(self):
        pass
    
    @abstractmethod
    def stop_loop(self):
        pass
    
    @abstractmethod
    async def disconnect(self):
        pass