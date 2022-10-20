#!/usr/bin/python
# Copyright 2022 TOSIT.IO
# SPDX-License-Identifier: Apache-2.0

import json
import xml.etree.ElementTree as ET
from collections import defaultdict

class FilterModule(object):

    def etree_to_dict(self, t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v
                         for k, v in dd.items()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v)
                            for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                  d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    def filters(self):
        return {
            'from_xml': self.from_xml,
            'xml_to_json': self.xml_to_json
        }

    def from_xml(self, data):
        root = ET.ElementTree(ET.fromstring(data)).getroot()
        return self.etree_to_dict(root)

    def xml_to_json(self, data):
        return json.dumps(self.from_xml(data))
