#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from operator import itemgetter

def get_event_times(root):
    first_elem = True
    last_segment_id = None
    oldtime = -1

    timed_events = [(int(e.attrib['Time']),e) for e in root.find('Events') if 'Time' in e.attrib and e.attrib['Time']]
    timed_events.sort(key=itemgetter(0))

    for t, event in timed_events:
        # check if time is monotonically increasing
        assert 'Time' in event.attrib
        assert t >= oldtime
        oldtime = t

        if event.tag.startswith('Mouse'):
            continue

        if 'SegId' in event.attrib and event.attrib['SegId'].startswith('t'):
            if first_elem:
                # time starts at 0 but no interface event for first sentence
                yield event.attrib['SegId'], 0
                first_elem = False

            last_segment_id = event.attrib['SegId']
            yield event.attrib['SegId'], t

        elif event.tag == 'Interface':
            # Interface event: change sentences
            # <Interface Time="3619231" Type="scroll segment" OldSegId="t1345798" NewSegId="t1345799"/>
            assert 'OldSegId' in event.attrib and 'NewSegId' in event.attrib

            # HACK: ignore repeated scroll events such as:
            # <Interface Time="2603015" Type="scroll segment" OldSegId="t1345766" NewSegId="t1345759"/>
            # <Interface Time="2603186" Type="scroll segment" OldSegId="t1345759" NewSegId="t1345752"/>
            # <Interface Time="2603305" Type="scroll segment" OldSegId="t1345759" NewSegId="t1345752"/>
            if last_segment_id == event.attrib['NewSegId']:
                sys.stderr.write("Ignoring: %s %s\n" %(event.tag, event.attrib))
                continue

            if last_segment_id != event.attrib['OldSegId']:
                last_segment_id = event.attrib['NewSegId']
                sys.stderr.write("Ignoring: %s %s\n" %(event.tag, event.attrib))
                continue

            assert last_segment_id == event.attrib['OldSegId']
            yield event.attrib['OldSegId'], t
            yield event.attrib['NewSegId'], t
            last_segment_id = event.attrib['NewSegId']
        elif event.tag == 'System' and 'Value' in event.attrib and event.attrib['Value'] == 'STOP':
            # End of Session
            # maybe repeated, thus ignored
            # <System Time="3658000" Value="STOP"/>
            pass

    yield -1, oldtime


def print_times_event(root, min_duration=2000):
    id2time = defaultdict(float)
    times = []
    last_segment_id = None
    for segment_id, time in get_event_times(root):
        times.append(time)
        if segment_id != last_segment_id:
            #print times
            if last_segment_id != None:
                if len(times)>2:
                    duration = (max(times) - min(times))
                    if duration >= min_duration:
                        id2time[last_segment_id] += (max(times) - min(times))
            times = [time]

        last_segment_id = segment_id

    for segment_id in sorted(id2time.keys()):
        print segment_id, id2time[segment_id]/1000.
    sys.stderr.write("Total: %s min\n" %(sum(id2time.values())/1000./60))

if __name__ == '__main__':
    tree = ET.parse(sys.stdin)
    root = tree.getroot()

    print_times_event(root)
