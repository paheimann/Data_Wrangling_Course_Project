#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

addr_keys = { }


def shape_element(element):
    node = {}
    created = {}
    address = {}
    node_refs = []
    if element.tag == "node" or element.tag == "way" :
        node.update([("type",element.tag)])
        lat = 0.
        lon = 0.
        #process first-level key-value pairs
        for key in element.attrib.keys():
            if key in CREATED:
                created.update([(key,element.attrib[key])])
            elif key == "lat":
                lat = float(element.attrib[key])
            elif key == "lon":
                lon = float(element.attrib[key])
            else:
                node.update([(key,element.attrib[key])])
        # process second-level elements
        for child in element:
            if child.tag == "tag":
                child_key = child.attrib["k"]
                child_value = child.attrib["v"]
                # ignore keys with problem characters
                if type(problemchars.search(child_key)) != type(None):
                    continue
                # process "addr:" key
                elif child_key.find("addr:") == 0: # key begins with "addr:"
                    addr_keys = child_key.split(":")
                    addr_key_1 = addr_keys[1]
                    if addr_key_1 == "postcode":
                        addr_key_1 = "zipcode"
                    if len(addr_keys) == 2:
                        address.update([(addr_key_1, child_value)])
                # process "amenity", "shop", "gnis:Class" keys
                elif child_key in ["amenity","shop","gnis:Class"]:
                    node.update([("place_type",child_value)])
                # process 3 other "gnis:" keys
                elif child_key.find("gnis:") == 0: # key begins with "gnis:"
                    gnis_keys = child_key.split(":")
                    if gnis_keys[1] in ["County","county_name"]:
                        address.update([("county",child_value)])
                    elif gnis_keys[1] == "ST_alpha":
                        address.update([("state",child_value)])
                # process "name" key for ways only
                elif element.tag == 'way' and child_key == "name":
                    node.update([("street",child_value)])
                # process 2 "tiger" keys
                elif child_key.find("tiger:") == 0: # key begins with "tiger:"
                    tiger_keys = child_key.split(":")
                    if tiger_keys[1] == "county":
                        address.update([("county",child_value)])
                    elif tiger_keys[1] == "zip_left":
                        address.update([("zipcode",child_value)])
                # process "county_name" key
                elif child_key == 'created_by':
                    created.update([("user",child_value)])
                # process "source" key
                elif child_key == 'source':
                    created.update([("user",child_value)])
                # process all other keys that pass through directly
                else:
                    node.update([(child_key, child_value)])
            elif child.tag == "nd":
                node_refs.append(child.attrib["ref"])
        # wrap up
        if lat != 0. and lon != 0.:
            pos = [lat,lon]
            node.update([("pos",pos)])
        if len(address) > 0:
            node.update([("address",address)])
        if len(node_refs) > 0:
            node.update([("node_refs",node_refs)])
        if len(created) >0:
            node.update([("created",created)])
        else:
            node.update([("created","None")])
        return node
        ##if len(node) > 3: ## For diagnostic purposes only, to omit location-only elements
        ##    return node  ## For diagnostic purposes only, to omit location-only elements
        ##else:  ## For diagnostic purposes only, to omit location-only elements
        ##    return None  ## For diagnostic purposes only, to omit location-only elements
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    #data = process_map('extract.osm', False)
    data = process_map('new_brunswick.osm', False)
    #pprint.pprint(data)

if __name__ == "__main__":
    test()