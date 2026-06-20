import xml.etree.ElementTree as et
import os
from conf.setting import FILE_PATH
from common.record_log import logs


class OperXML:

    def read_xml(self, filename, tags, attr_value):
        """
        Read an XML element value.
        :param filename: XML file name; no path is required.
        :param tags: XML element name to read.
        :param attr_value: Element attribute value, such as an id, name, or class.
        :return:
        """
        root = ''
        file_path = {
            'file': os.path.join(FILE_PATH['XML'], filename)
        }
        try:
            tree = et.parse(file_path['file'])
            # Get the XML root element.
            root = tree.getroot()
        except Exception as e:
            logs.error(e)

        child_text = ''
        # Traverse the entire XML file.
        for child in root.iter(tags):

            att = child.attrib

            if ''.join(list(att.values())) == attr_value:
                child_text = child.text.strip()
            if child:
                for i in child:
                    attr = i.attrib
                    if ''.join(list(attr.values())) == attr_value:
                        child_text = i.text.strip()

        return child_text

    def get_attribute_value(self, filename, tags):
        """
        Read element attribute values.
        :param filename: File path.
        :param tags: XML element name.
        :return: Dictionary.
        """

        root = ''
        file_path = {'file': os.path.join(FILE_PATH['RESULTXML'], filename)}
        try:
            tree = et.parse(file_path['file'])
            # Get the XML root element.
            root = tree.getroot()
        except Exception as e:
            logs.error(e)

        attr = [child.attrib for child in root.iter(tags)][0]

        return attr
