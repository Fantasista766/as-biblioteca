from dataclasses import dataclass
from typing import Callable


@dataclass
class Policy:
    action: str
    check: Callable[[dict[str, any], dict[str, any]], bool]


class AccessManager:
    def __init__(self) -> None:
        self.policies: list[Policy] = []

    def add_policy(
        self, action: str, rule: Callable[[dict[str, any], dict[str, any]], bool]
    ) -> None:
        self.policies.append(Policy(action, rule))

    def check(
        self, action: str, subject: dict[str, any], resource: dict[str, any] | None = None
    ) -> bool:
        resource = resource or {}
        for policy in self.policies:
            if policy.action == action and policy.check(subject, resource):
                return True
        return False


access_manager = AccessManager()


def init_default_policies() -> None:
    """Инициализация стандартных политик"""
    access_manager.add_policy(
        "user:edit",
        lambda sub, obj: sub.get("id") == obj.get("owner_id") or sub.get("role") == "admin",
    )


init_default_policies()
