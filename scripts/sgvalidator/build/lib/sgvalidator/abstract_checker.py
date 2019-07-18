from abc import ABC, abstractmethod


class AbstractChecker(ABC):
    @abstractmethod
    def check(self):
        pass
