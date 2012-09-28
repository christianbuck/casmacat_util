#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
from editor import Editor

def get_text(root, tag):
    subtree = root.find(tag)
    for element in subtree:
        if not element.tag == 'Seg':
            continue
        segment_id = element.attrib['Id']
        if element.text:
            yield element.text.replace('\n',' '), segment_id
        else:
            yield "", segment_id

def get_log(root):
    for event in root.find('Events'):
        #<Key Time="39449" Cursor="0" Type="insert" Value="S" SegId="t1346816"/>
        yield event.tag, event.attrib

#def get_src(root):
#    source_segments = {}
#    src_path = 'Project/Interface/Standard/Settings/SourceText'
#    for src, src_id in get_text(root, src_path):
#        source_segments[src_id] = src
#    return source_segments
#
#def get_tgt(root):
#    target_segments = {}
#    path = 'Project/Interface/Standard/Settings/TargetText'
#    for tgt, tgt_id in get_text(root, path):
#        target_segments[tgt_id] = tgt.encode('latin-1')
#    return target_segments

def get_segments(root, path):
    segments = {}
    for segment, segment_id in get_text(root, path):
        segments[segment_id] = segment.encode('latin-1')
    return segments

if __name__ == '__main__':
    tree = ET.parse(sys.stdin)
    root = tree.getroot()

    target_segments = get_segments(root, 'Project/Interface/Standard/Settings/TargetText')
    final_segments = get_segments(root, 'FinalText')
    print target_segments

    editors = {}

    edited_segments = {}
    for event_tag, attribs in get_log(root):
        if event_tag == 'Key':
            segment_id = attribs['SegId']

            if not segment_id in editors:
                editors[segment_id] = Editor(target_segments[segment_id])
            e = editors[segment_id]

            pos = int(attribs['Cursor'])

            assert attribs['Type'] in ['insert','delete']
            if attribs['Type'] == 'insert':
                if attribs.get('Text', None):
                    text = attribs['Text'].encode('latin-1')
                    e.delete(pos, text)
                text = attribs['Value'].encode('latin-1')
                e.insert(pos, text)
            elif attribs['Type'] == 'delete':
                assert attribs['Value'] in ['[Delete]', '[Back]']
                if len(attribs['Text']) > 1 and attribs['Text'][0] == ' ':
                    pos += 1
                    attribs['Text'] = attribs['Text'][1:]
                #text = ''.join(reversed(attribs['Text'].strip()))
                #text = unicode(attribs['Text'])
                text = attribs['Text'].encode('latin-1')
                if attribs['Value'] == '[Delete]' or '[Back]':
                    e.delete(pos, text)
                else:
                    e.backspace(pos, text)

            #print repr(e.text)
            #print repr(str(e))
            #s = str(e)
            edited_segments[segment_id] = str(e)
            print str(e).decode('latin-1')

    for segment_id in edited_segments:
        assert edited_segments[segment_id] == final_segments[segment_id]
        assert edited_segments[segment_id].decode('latin-1') == final_segments[segment_id].decode('latin-1')
