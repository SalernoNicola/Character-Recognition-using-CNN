from abc import ABC, abstractmethod


class BWriter(ABC):

    @abstractmethod
    def write_instance(self, item):
        pass
