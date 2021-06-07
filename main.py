# import logging
from dataclasses import dataclass, field
from fastapi import FastAPI
from ariadne.asgi import GraphQL
from ariadne import (
    ObjectType,
    QueryType,
    MutationType,
    EnumType,
    InterfaceType,
    make_executable_schema,
    load_schema_from_path,
    convert_kwargs_to_snake_case,
    snake_case_fallback_resolvers,
    SchemaDirectiveVisitor
)
from graphql import default_field_resolver
from uuid import uuid4
from enum import Enum
import re

# logging.basicConfig(level=logging.DEBUG)


class FixedLengthDirective(SchemaDirectiveVisitor):
    def visit_input_field_definition(self, field, object_type):
        print("#######", field, dir(field))
        n = self.args.get("n")
        # original_resolver = field.resolve or default_field_resolver

        # def resolve_fixed_sequence(obj, info, **kwargs):
        #     result = original_resolver(obj, info, **kwargs)
        #     if result is None:
        #         return None

        #     if len(result) != n:
        #         raise TypeError("fixed length")

        #     return result

        # field.resolve = resolve_fixed_sequence
        return field


def idgen(prefix):
    return lambda: f"{prefix}:{uuid4()}"


@dataclass
class RunnerDef:
    name: str
    variant: str
    id: str = field(default_factory=idgen("RunnerDef"))


class SkillKind(Enum):
    UNIQUE = "UNIQUE"
    GOLD = "GOLD"
    WHITE = "WHITE"


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
class Skill:
    name: str
    kind: SkillKind
    id: str = field(default_factory=idgen("Skill"))


@dataclass
class Runner:
    runner_def_id: int
    apt_ground: [AptRank]
    apt_distance: [AptRank]
    apt_position: [AptRank]
    status: [int]
    skills: [Skill] = field(default_factory=list)
    id: str = field(default_factory=idgen("Runner"))


runner_defs: [RunnerDef] = [
    RunnerDef("ゴールドシップ", "レッドストライフ"),
    RunnerDef("メジロマックイーン", "エレガンス・ライン"),
    RunnerDef("メジロマックイーン", "エンド・オブ・スカイ"),
]

runners = []

skills = []

query = QueryType()
mutation = MutationType()
runner = ObjectType("Runner")
user = ObjectType("User")
# create_runner_input = ObjectType("CreateRunnerInput")


def find(fn, lst):
    return next(filter(fn, lst), None)


@query.field("hello")
def resolve_hello(*_):
    return "Hello, GraphQL!"


@query.field("runner")
def resolve_runner(_, info, id: str):
    runner = find(lambda x: x.id == id, runners)

    if runners:
        runner_def = find(
            lambda x: x.id == runner.runner_def_id, runner_defs)

        return {
            "id": id,
            "runner_def_id": runner.runner_def_id,
            "name": runner_def.name,
            "variant": runner_def.variant,
            "apt_ground": runner.apt_ground,
            "apt_distance": runner.apt_distance,
            "apt_position": runner.apt_position,
            "status": runner.status,
            "skills": runner.skills
        }

    return None


@runner.field("name")
def resolve_runner_name(obj, info):
    print("hogehoge")
    return "トウカイテイオー"


@query.field("user")
def resolve_user(obj, info):
    return {
        "id": "1",
        "name": "foo"
    }


@user.field("name")
def resolve_user_name(obj, info):
    print("fugafuga")
    return "bar"


@query.field("runnerDefs")
def resolve_runner_defs(obj, info) -> [RunnerDef]:
    # print(obj)
    # print(info)
    return runner_defs


@query.field("skills")
def resolve_skills(obj, info) -> [RunnerDef]:
    # print(obj)
    # print(info)
    return skills


@query.field("runnerDef")
def resolve_runner_def(obj, info, id):
    runner_def = find(lambda x: x.id == id, runner_defs)

    if runner_def:
        return runner_def

    return None


node = InterfaceType("Node")


@query.field("node")
def resolve_node(obj, info, id):
    # ID のプレフィクスに対応したオブジェクトを検索して返す
    if m := re.match(r"(\w+):", id):
        node_type = m.groups()[0]

        resolver_map = {
            "Runner": resolve_runner,
            "RunnerDef": resolve_runner_def
        }

        if node_type in resolver_map:
            # 型リゾルバに返却させる型をコンテキストで渡す
            info.context["node_type"] = node_type

            return resolver_map[node_type](obj, info, id)

    return None


@node.type_resolver
def resolve_node_type(obj, info, _):
    return info.context.get("node_type")


skill_kind = EnumType("SkillKind", SkillKind)
apt_rank = EnumType("AptRank", AptRank)


@mutation.field("createSkill")
def resolve_create_skill(obj, info, name, kind):
    print(skills, kind, type(kind), SkillKind(kind), type(SkillKind(kind)))
    new_skill = Skill(name, SkillKind(kind))
    skills.append(new_skill)
    return new_skill


@dataclass
class CreateRunnerInput:
    runner_def_id: str
    apt_grount: [AptRank]
    apt_distance: [AptRank]
    apt_position: [AptRank]
    status: [int]
    skills: [Skill]


@mutation.field("createRunner")
@convert_kwargs_to_snake_case
def resolve_create_runner(obj, info, input):
    print(input)
    new_runner = Runner(
        input["runner_def_id"],
        input["apt_ground"],
        input["apt_distance"],
        input["apt_position"],
        input["status"],
        input["skills"],
    )
    runners.append(new_runner)

    runner_def = find(
        lambda x: x.id == input["runner_def_id"], runner_defs)

    return {
        "id": new_runner.id,
        "name": runner_def.name,
        "variant": runner_def.variant,
        "apt_ground": new_runner.apt_ground,
        "apt_distance": new_runner.apt_distance,
        "apt_position": new_runner.apt_position,
        "status": new_runner.status,
        "skills": new_runner.skills
    }


type_defs = load_schema_from_path("schema.graphql")

schema = make_executable_schema(
    type_defs, query, runner, user, node, mutation, skill_kind, snake_case_fallback_resolvers,
    directives={"fixedLength": FixedLengthDirective})

app = FastAPI()
app.add_route("/graphql", GraphQL(schema, debug=True))


@app.get("/")
async def root():
    return {"message": "Hello, World!"}
