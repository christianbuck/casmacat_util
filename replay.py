#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
from editor import Editor, EditException, SeriousEditException

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
        segments[segment_id] = prep(segment)
    return segments

def prep(text):
    #print text.encode('latin-1').replace('&','&amp;')
    return text.encode('latin-1').replace('&','&amp;')

if __name__ == '__main__':
    tree = ET.parse(sys.stdin)
    root = tree.getroot()

    target_segments = get_segments(root, 'Project/Interface/Standard/Settings/TargetText')
    final_segments = get_segments(root, 'FinalText')
    #print target_segments

    editors = {}

    edited_segments = {}
    error_ids = set()
    for event_tag, attribs in get_log(root):
        print attribs['Time']
        print attribs
        if event_tag == 'Key':
            segment_id = attribs['SegId']

            if not segment_id in editors:
                editors[segment_id] = Editor(target_segments.get(segment_id,""))
            e = editors[segment_id]

            pos = int(attribs['Cursor'])

            assert attribs['Type'] in ['insert','delete']
            #if not 'Value' in attribs:
            #    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$No Value, skipping'
            #el
            if attribs['Type'] == 'insert':
                if attribs.get('Text', None):  # Text is selected
                    text = prep(attribs['Text'])
                    if e.check_delete(pos, text):
                        e.delete(pos, text)
                    elif 'Value' in attribs:   # deleting nothing is ok, if we don't insert anything
                        error_ids.add(segment_id)
                    else:
                        print 'UNDELETED:', text
                text = prep(attribs.get('Value',''))
                e.insert(pos, text)
                #text = prep(attribs.get('Value',''))
                #e.insert(pos, text)
            elif attribs['Type'] == 'delete':
                assert attribs['Value'] in ['[Delete]', '[Back]']
                #if len(attribs['Text']) > 1 and attribs['Text'][0] == ' ':
                #    pos += 1
                #    attribs['Text'] = attribs['Text'][1:]
                if len(attribs['Text']) == 2:
                    if attribs['Text'][0] == ' ':
                        pos += 1
                        attribs['Text'] = attribs['Text'][1:]
                    if attribs['Text'][-1] == ' ':
                        attribs['Text'] = attribs['Text'][:-1]
                elif len(attribs['Text']) > 2 and attribs['Text'].startswith(' '): # was 2 spaces
                    #print 'dont delete!'
                    pos += 1
                    attribs['Text'] = attribs['Text'][1:]

                #text = ''.join(reversed(attribs['Text'].strip()))
                #text = unicode(attribs['Text'])
                text = prep(attribs['Text'])
                try:
                    #if attribs['Value'] == '[Delete]' or '[Back]':
                    if e.check_delete(pos, text):
                        e.delete(pos, text)
                    elif e.check_backspace(pos, text):
                        print 'TRYING BACKSPACE'
                        e.backspace(pos, text)
                    else:
                        raise EditException('could not delete')
                        raise SeriousEditException('could not delete')
                except EditException:
                    error_ids.add(segment_id)
            #print repr(e.text)
            #print repr(str(e))
            #s = str(e)
            #edited_segments[segment_id] = str(e)
            #print str(e).decode('latin-1')
            s = str(e).decode('latin-1').encode('utf-8')
            edited_segments[segment_id] = s
            print str(e).decode('latin-1').encode('utf-8')
            #print str(e).encode('utf-8')

    print "Error in segments:", " ".join(error_ids)
    for segment_id in edited_segments:
        print segment_id
        print target_segments[segment_id].decode('latin-1').replace('&amp;','&').encode('utf-8')
        print edited_segments[segment_id]
        print final_segments[segment_id].decode('latin-1').replace('&amp;','&').encode('utf-8')
        if not (segment_id in error_ids or edited_segments[segment_id] == final_segments[segment_id].decode('latin-1').replace('&amp;','&').encode('utf-8')):
            print "ERROR, final and edited don't match"
            error_ids.add(segment_id)
        assert segment_id in error_ids or edited_segments[segment_id] == final_segments[segment_id].decode('latin-1').replace('&amp;','&').encode('utf-8')

    print "Error in segments:", " ".join(error_ids)
    print "found errors in %s of %s segments" %(len(error_ids), len(final_segments))
    #    assert edited_segments[segment_id].decode('latin-1') == final_segments[segment_id].decode('latin-1')

    #    print edited_segments[segment_id].decode('latin-1')
    #    print final_segments[segment_id].decode('latin-1')
    #    #assert edited_segments[segment_id] == final_segments[segment_id]
    #    assert edited_segments[segment_id].decode('latin-1') == final_segments[segment_id].decode('latin-1')
