import codecs
import os
from lxml import etree
import xml.etree.ElementTree as eltree
from xml.etree.ElementTree import Element, SubElement

XML_EXT = '.xml'
ENCODE_METHOD = 'utf-8'
JPG_EXT = '.jpg'

class XMLGenerator:
    def __init__(self):
        pass


    def prettify(self, elem):
        rough_string = eltree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding=ENCODE_METHOD).replace("  ".encode(), "\t".encode())


    def generate(self, foldername, filename, imgsize, box_list):
        if foldername is None or filename is None or imgsize is None:
            return None
        
        top = Element('annotation')
        folder = SubElement(top, 'folder')
        folder.text = foldername

        ele_filename = SubElement(top, 'filename')
        ele_filename.text = filename + '.jpg'

        size = SubElement(top, 'size')
        height, width = imgsize
        ele_width = SubElement(size, 'width')
        ele_width.text = str(width)
        ele_height = SubElement(size, 'height')
        ele_height.text = str(height)

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'

        for obj in box_list:
            #print(obj)
            name, xmin, ymin, xmax, ymax = obj
            ele_object = SubElement(top, 'object')
            obj_name = SubElement(ele_object, 'name')
            obj_name.text = name
            pose = SubElement(ele_object, 'pose')
            pose.text = 'unspecified'
            truncated = SubElement(ele_object, 'truncated')
            truncated.text = '0'
            difficult = SubElement(ele_object, 'difficult')
            difficult.text = '0'

            bndbox = SubElement(ele_object, 'bndbox')
            ele_xmin = SubElement(bndbox, 'xmin')
            ele_xmin.text = str(xmin)
            ele_ymin = SubElement(bndbox, 'ymin')
            ele_ymin.text = str(ymin)
            ele_xmax = SubElement(bndbox, 'xmax')
            ele_xmax.text = str(xmax)
            ele_ymax = SubElement(bndbox, 'ymax')
            ele_ymax.text = str(ymax)
        
        return top


    def save_xml(self, foldername, filename, imgsize, box_list, xml_dir):
        xml = self.generate(foldername, filename, imgsize, box_list)
        if xml:
            prettify_result = self.prettify(xml)
            xml_file = codecs.open(os.path.join(xml_dir, filename + XML_EXT), 'w', encoding=ENCODE_METHOD)
            xml_file.write(prettify_result.decode('utf-8'))
            xml_file.close()


    def copy_xml(self, src_xml, dest_xml, xml_dir):
        src_xml = open(os.path.join(xml_dir, src_xml + XML_EXT))
        top = eltree.parse(src_xml)
        root = top.getroot()

        filename = root.findall('filename')[0]
        filename.text = dest_xml + JPG_EXT

        top.write(os.path.join(xml_dir, dest_xml + XML_EXT))