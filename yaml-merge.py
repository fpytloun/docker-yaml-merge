#!/usr/bin/env python3

import argparse
import logging
import os
import yaml
import sys

logging.basicConfig()
lg = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser("yaml-merge")
    group_common = parser.add_argument_group("Common")
    group_common.add_argument('-v', '--verbose', action="store_true")
    group_common.add_argument('-d', '--debug', action="store_true")
    group_common.add_argument('--dry', '--dry-run', action="store_true")
    group_common.add_argument('-o', '--output', default="-")
    group_common.add_argument('--extension', nargs='+', default=["yaml", "yml"])
    group_common.add_argument('file', nargs='+')
    args = parser.parse_args()
    return args

def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        elif isinstance(value, list):
            destination.setdefault(key, [])
            destination[key].extend(value)
        else:
            destination[key] = value
    return destination

def main():
    args = parse_args()

    if args.verbose:
        lg.setLevel(logging.INFO)

    if args.debug:
        lg.setLevel(logging.DEBUG)

    data = {}
    for entry in args.file:
        if os.path.isfile(entry):
            if os.path.splitext(entry)[1] not in args.extension:
                lg.debug("Skipping file {} not matching extensions {}".format(entry, args.extension))
                continue
            lg.info("Merging file {}".format(entry))
            with open(entry, 'r') as fh:
                merge(yaml.load(fh), data)
        else:
            lg.info("Traversing directory structure {}".format(entry))
            for root, dirs, files in os.walk(entry):
                for f in files:
                    if os.path.splitext(f)[1].replace('.', '') not in args.extension:
                        lg.debug("Skipping file {} not matching extensions {}".format(f, args.extension))
                        continue
                    path = os.path.join(root, f)
                    lg.info("Merging file {}".format(path))
                    with open(path, 'r') as fh:
                        merge(yaml.load(fh), data)

    if data:
        if args.output == "-":
            print(yaml.dump(data))
        else:
            with open(args.output, 'w') as fh:
                yaml.dump(data, fh)
    else:
        lg.error("No merged data")
        sys.exit(1)

if __name__ == '__main__':
    main()
