from abc import ABC, abstractmethod

class ISerial(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def set_receiver(self, callback):
        pass

    @abstractmethod
    def queue_write(self, value: bytes):
        pass

    @abstractmethod
    async def run_loop(self):
        pass

    @abstractmethod
    def stop_loop(self):
        pass

    @abstractmethod
    def remove(self):
        pass