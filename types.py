import re
from dataclasses import dataclass, field
from uuid import uuid4


# def resolve_node(obj, info, id):
#     if m := re.match(r"(\w)+:", id):
#         prefix = m.groups()[0]

#         dispatch_table = {
#             "Skill": resolve_skill,
#             "Runner": resolve_runner,
#             "RunnerDef": resolve_runner_def
#         }

#         if prefix in dispatch_table:
#             return dispatch_table[prefix](obj, info, id)

#     return None


def node_id(prefix: str):
    return field(default_factory=lambda: prefix + str(uuid4()))


class AptRank(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


@dataclass
class Runner:
    name: str
    variant: str
    apt_ground: [AptRank]
    apt_distance: [AptRank]
    apt_position: [AptRank]
    status: [int]
    id: str = node_id("Runner")
