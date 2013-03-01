"""
Telepyhton exports Python modules to XML. You send a query to Telepython, and
it returns the result of a method in XML.

Author: Adam Victor Brandizzi <brandizzi+telepython@gmail.com>
"""

import json
from xml.etree.ElementTree import Element, tostring

class XMLInterface(object):
    def __init__(self, module):
        self.module = module
        self.complex_objects = {}
        self.next_id = 1
        self.current_search_state = set()

    def call(self, name, *args, **kwargs):
        try:
            result = self.get_value(name, *args, **kwargs)
        except Exception, e:
            doc = self.get_raised_xml(e)
        else:
            doc = self.get_xml(result)
        return doc
    
    def get(self, name):
        try:
            attribute = self.get_attribute(self.module, name)
        except Exception, e:
            attribute = e
        doc = self.get_xml(attribute)
        return doc
    
    def get_attribute(self, source, name):
        if '.' not in name:
            return getattr(source, name)
        chain = name.split('.', 1)
        new_source = getattr(source, chain[0])
        return self.get_attribute(new_source, chain[1])
        
    
    def get_by_id(self, _id):
        found = [value[1] 
            for key, value in self.complex_objects.items() 
            if value[0] == _id]
        if found:
            return self.get_xml(found[0])
    
    def get_value(self, name, *args, **kwargs):
        attribute = getattr(self.module, name)
        arguments = [json.read(arg) for arg in args]
        kwarguments = dict( (key, json.read(value)) for key, value in kwargs.items())
        result = attribute(*arguments, **kwarguments)
        return result
    
    def get_xml(self, result):
        self.current_search_state = set()
        xml = '<?xml version="1.0"?>'
        xml += tostring(self.converted(result))
        return xml
    
    def get_raised_xml(self, exception):
        self.current_search_state = set()
        self.add_to_complex_objects(exception)
        element = Element('raise', 
                exception=exception.__class__.__name__,
                id=self.get_object_id(exception))
        message_element = Element('message')
        message_element_value = self.converted(exception.message)
        message_element.append(message_element_value)
        element.append(message_element)
        xml = '<?xml version="1.0"?>'
        xml += tostring(element)
        return xml
    
    def converted(self, result):
        if type(result) == int:
            element = Element('int', value=str(result))
        elif type(result) == float:
            element = Element('float', value=str(result))
        elif type(result) == str:
            element = Element('str', value=result)
        elif type(result) == list or type(result) == tuple:
            self.add_to_complex_objects(result)
            element = Element(result.__class__.__name__, id=self.get_object_id(result))
            self.add_list_elements(element, result)
        elif type(result) == dict:
            self.add_to_complex_objects(result)
            element = Element('dict', id=self.get_object_id(result))
            self.add_dict_elements(element, result)
        elif result is None:
            element = Element('None')
        elif isinstance(result, object):
            self.add_to_complex_objects(result)
            element = Element(result.__class__.__name__, id=self.get_object_id(result))
            self.add_object_elements(element, result)
        else:
            element = Element('none')
        return element
            
    def add_to_complex_objects(self, obj):
        id_key = id(obj)
        if id_key not in self.complex_objects:
            self.complex_objects[id_key] = (str(self.next_id), obj)
            self.next_id += 1

    def add_list_elements(self, element, _list):
        id_key = id(_list)
        if id_key not in self.current_search_state:
            self.current_search_state.add(id_key)
            for value in _list:
                element.append(self.converted(value))

    def add_dict_elements(self, element, _dict):
        id_key = id(_dict)
        if id_key not in self.current_search_state:
            self.current_search_state.add(id_key)
            items = _dict.items()
            items.sort()
            for key, value in items:
                key_element = Element('key')
                key_element_value = self.converted(key)
                key_element.append(key_element_value)
                
                value_element = Element('value')
                value_element_value = self.converted(value)
                value_element.append(value_element_value)
                
                element.append(key_element)
                element.append(value_element)

    def add_object_elements(self, element, obj):
        id_key = id(obj)
        if id_key not in self.current_search_state:
            self.current_search_state.add(id_key)
            attributes = [attr for attr in dir(obj)
                if not attr.startswith('_') and not callable(getattr(obj, attr))]
            attributes.sort()
            for attribute in attributes:
                attribute_element = Element(attribute)
                
                attribute_element_value = self.converted(getattr(obj, attribute))
                attribute_element.append(attribute_element_value)
                
                element.append(attribute_element)

    def get_object_id(self, obj):
        id_key = id(obj)
        return self.complex_objects[id_key][0]

def xml_module(module):
    xml_interface = XMLInterface(module)
    return xml_interface

if __name__ == "__main__":
    import doctest
    doctest.testfile("telepython.txt")

