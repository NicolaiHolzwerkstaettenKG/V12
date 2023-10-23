# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import json


class XsdComplexType:

    @staticmethod
    def validate(data: dict):
        pass

    def mindict(self, data):
        clean = {}
        for k in data:
            val = data[k]
            if not val:
                continue
            elif type(val) is dict:
                clean[k] = self.mindict(val)
            elif type(val) is list:
                sublist = []
                for v in val:
                    subval = self.mindict(v)
                    if subval:
                        sublist.append(subval)
                clean[k] = sublist
            else:
                clean[k] = val
        return clean

    def json_data(self) -> str:
        return json.dumps(self.mindict(self.data))
