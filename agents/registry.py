import importlib
import pkgutil
import agents
from agents.base import BaseAgent


def discover_agents() -> dict[str, "BaseAgent"]:
    """Auto-discover every BaseAgent subclass in the agents/ package."""
    for _, module_name, _ in pkgutil.iter_modules(agents.__path__):
        if module_name in ("base", "registry"):
            continue
        importlib.import_module(f"agents.{module_name}")

    registry: dict[str, BaseAgent] = {}
    for cls in BaseAgent.__subclasses__():
        if cls.name:
            registry[cls.name] = cls()

    return registry
