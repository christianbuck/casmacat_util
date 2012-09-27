#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET

def get_text(root, tag):
    subtree = root.find(tag)
    for element in subtree:
        if element.text:
            yield element.text.replace('\n',' ')
        else:
            yield ""

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('type', choices=['all', 'src', 'tgt', 'final'])
    args = parser.parse_args(sys.argv[1:])

    tree = ET.parse(sys.stdin)
    root = tree.getroot()
    
    src = list(get_text(root, 'Project/Interface/Standard/Settings/SourceText'))
    tgt = list(get_text(root, 'Project/Interface/Standard/Settings/TargetText'))
    final = list(get_text(root, 'FinalText'))

    for s, t, f in zip(src, tgt, final):
        if args.type in ['all', 'src']:
            print s.encode('utf-8')
        if args.type in ['all', 'tgt']:
            print t.encode('utf-8')
        if args.type in ['all', 'final']:
            print f.encode('utf-8')
