#!/usr/bin/env python3

import argparse
import logging
import os
import yaml
import sys
import re

logging.basicConfig()
lg = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser("yaml-merge")
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-o', '--output', default="-", help="Output file, defaults to stdout")
    parser.add_argument('--extension', nargs='+', default=["yaml", "yml"], help="List of extensions, defaults to yml, yaml. Can be 'any' to skip check")
    parser.add_argument('--filter', help="Regular expression to filter keys for merging")
    parser.add_argument('-b', '--base', help="Base file to merge other into, useful with --filter parameter")
    parser.add_argument('file', nargs='+')
    args = parser.parse_args()
    return args

def merge(source, destination, regex=None):
    for key, value in source.items():
        if regex and not regex.search(key):
            continue
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node, regex)
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

    if args.filter:
        regex = re.compile(args.filter)
    else:
        regex = None

    if args.base:
        with open(args.base, 'r') as fh:
            data = yaml.load(fh)
    else:
        data = {}
    for entry in args.file:
        if os.path.isfile(entry):
            if os.path.splitext(entry)[1].replace('.', '') not in args.extension and "any" not in args.extension:
                lg.debug("Skipping file {} not matching extensions {}".format(entry, args.extension))
                continue
            lg.info("Merging file {}".format(entry))
            with open(entry, 'r') as fh:
                merge(yaml.load(fh), data, regex)
        else:
            lg.info("Traversing directory structure {}".format(entry))
            for root, dirs, files in os.walk(entry):
                for f in files:
                    if os.path.splitext(f)[1].replace('.', '') not in args.extension and "any" not in args.extension:
                        lg.debug("Skipping file {} not matching extensions {}".format(f, args.extension))
                        continue
                    path = os.path.join(root, f)
                    lg.info("Merging file {}".format(path))
                    with open(path, 'r') as fh:
                        merge(yaml.load(fh), data, regex)

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
