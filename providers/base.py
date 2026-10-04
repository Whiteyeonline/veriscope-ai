"""
providers/base.py
Base Abstract Class for Data Providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvider(ABC):
    def __init__(self, name: str, requires_key: bool = False, priority: int = 1):
        self.name = name
        self.requires_key = requires_key
        self.priority = priority
        self.enabled = True

    @abstractmethod
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        pass
