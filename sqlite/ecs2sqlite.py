#!/usr/bin/env python

import pandas
import numpy
import sqlite3
import json
import argparse
import ipaddress
from itertools import groupby
from uuid import UUID


DROPPED = [
    "agent.ephemeral_id",
    "destination.bytes",
    "destination.domain",
    "destination.packets",
    "source.bytes",
    "source.domain",
    "source.packets",
    "message",
    "related.hash",
    "related.ip",
    "related.user",
    "error.code",
    "ecs.version",
    "rule.name",
    "event.end",
    "event.ingested",
    "event.kind",
    "event.module",
    "event.provider",
    "event.sf_ret",
    "event.sf_type",
    "event.duration",
    "event.start",
    "file.code_signature.status",
    "file.code_signature.subject_name",
    "file.code_signature.valid",
    "file.hash.md5",
    "file.hash.sha1",
    "file.pe.company",
    "file.pe.description",
    "file.pe.file_version",
    "file.pe.imphash",
    "file.pe.original_file_name",
    "file.pe.product",
    "file.target_path",
    "file.type",
    "network.iana_number",
    "network.transport",
    "network.type",
    "network.direction",
    "process.start",
    "process.args_count",
    "process.hash.md5",
    "process.hash.sha1",
    "process.parent.args_count",
    "process.pe.company",
    "process.pe.description",
    "process.pe.file_version",
    "process.pe.imphash",
    "process.pe.original_file_name",
    "process.pe.product",
    "process.parent.args",
    "process.parent.command_line",
    "process.parent.executable",
    "process.parent.start",
    "process.thread.id",
    "process.working_directory",
    "user.group.id",
    "user.group.name",
]

DROPPEDPREFIX = ["winlog.", "sf_file_action."]

INTCOLS = [
    "network.bytes",
    "source.port",
    "destination.port",
    "process.pid",
    "process.parent.pid",
]

# condense a list of values into one value to get rid of list
FUNNEL = {
    frozenset(["start", "connection", "protocol"]): "start",
    frozenset(["configuration", "registry"]): "registry",
}


def delist(col):
    if col == "host.ip":
        return get_ipv4
    elif col in ("process.args", "process.parent.args"):
        return concat_list
    else:
        return generic_delist


def generic_delist(x):
    if isinstance(x, list):
        if len(x) == 1:
            return x[0]
        elif frozenset(x) in FUNNEL:
            return FUNNEL[frozenset(x)]
        else:
            raise Exception("multiple items in list: ", x)
    else:
        return x


def get_ipv4(xs):
    if isinstance(xs, list):
        ys = list(
            filter(
                lambda x: isinstance(x, ipaddress.IPv4Address),
                map(ipaddress.ip_address, xs),
            )
        )
        if len(ys) > 1:
            raise Exception("multiple IPv4 found: ", xs)
        else:
            return str(ys[0])
    else:
        return xs


def concat_list(xs):
    if isinstance(xs, list):
        return " ".join(xs)
    else:
        return xs


def unwrap_bracket(x):
    return x[1:-1] if isinstance(x, str) and x[0] == "{" and x[-1] == "}" else x


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db")
    parser.add_argument("table")
    parser.add_argument("inputjsons", nargs="+")
    args = parser.parse_args()

    rows = []
    for inputjson in args.inputjsons:
        with open(inputjson) as ndj:
            for jsonline in ndj.readlines():
                rows.append(json.loads(jsonline)["_source"])

    # init data
    df = pandas.json_normalize(rows)

    # drop unused data
    df = df.drop(columns=DROPPED)
    for PREFIX in DROPPEDPREFIX:
        df = df.drop(columns=[col for col in list(df) if col.startswith(PREFIX)])
    # transform some columns
    for c in df:
        df[c] = df[c].apply(delist(c))
    # unwrap process UUID (fix sysmon data)
    df["process.entity_id"] = df["process.entity_id"].apply(unwrap_bracket)
    df["process.parent.entity_id"] = df["process.parent.entity_id"].apply(
        unwrap_bracket
    )
    # fix float->int issue
    for c in INTCOLS:
        df[c] = df[c].fillna(-1).astype(int)
    # add process UUID is not exist (fix sysflow data)
    df["process.entity_id"] = df.apply(
        lambda x: (
            str(UUID(int=x["process.pid"]))
            if x["process.pid"] >= 0 and x["process.entity_id"] is numpy.nan
            else x["process.entity_id"]
        ),
        axis=1,
    )
    df["process.parent.entity_id"] = df.apply(
        lambda x: (
            str(UUID(int=x["process.parent.pid"]))
            if x["process.parent.pid"] >= 0
            and x["process.parent.entity_id"] is numpy.nan
            else x["process.parent.entity_id"]
        ),
        axis=1,
    )

    # print preview
    for k, g in groupby(sorted(list(df)), lambda x: x.split(".")[0]):
        cols = list(g)
        print(f"# Example row for {k}:")
        print(df[df[cols].notna().all(axis=1)][cols].iloc[0])
        print()

    # fill NaN
    df = df.fillna("")

    # write to db
    con = sqlite3.connect(args.db)
    df.to_sql(args.table, con=con, if_exists="replace")
