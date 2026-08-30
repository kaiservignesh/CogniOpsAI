from abc import ABC, abstractmethod


class ActionAdapter(ABC):
    @abstractmethod
    def execute(
        self,
        payload: dict,
    ) -> str:
        raise NotImplementedError