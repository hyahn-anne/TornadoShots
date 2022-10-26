import os
import cv2
import random
import numpy as np
import shutil
import albumentations as A
import imgaug.augmenters as iaa
from datetime import datetime
from PIL import Image
from libs.xml_generator import XMLGenerator

JPG_EXT = '.jpg'
XML_EXT = '.xml'

class Simulator:
    IMG_DIR_NAME = 'images'
    XML_DIR_NAME = 'xmls'
    FILTER_DIR_NAME = 'filtered'


    def __init__(self):
        self.png_path = ''
        self.png_list = []
        self.background_path = ''
        self.background_list = []
        self.is_set = False
        self.bg_ready = False
        self.png_ready = False
        self.simulation_images = []
        self.is_simulation = False
        self.xml_generator = XMLGenerator()

        # section mapping: top=1, left=2, bottom=3, right=4
        self.section = {'1': (0, 0), '2': (0, 0), '3': (0, 0), '4': (0, 0)}

        self.br = (0, 0)
        self.cr = (0, 0)
        self.temp = (0, 0)
        self.filter_list = ['brightness', 'contrast', 'temperature', 'all']


    def divide(self, rects):
        if len(rects) > 0:
            r0_xmin, r0_ymin, r0_xmax, r0_ymax = rects['0']
            r1_xmin, r1_ymin, r1_xmax, r1_ymax = rects['1']

            left = (r0_xmin, r1_xmin, r0_ymin, r0_ymax)
            right = (r1_xmax, r0_xmax, r0_ymin, r0_ymax)
            top = (r1_xmin, r1_xmax, r0_ymin, r1_ymin)
            bottom = (r1_xmin, r1_xmax, r1_ymax, r0_ymax)

            self.section['1'] = top
            self.section['2'] = left
            self.section['3'] = bottom
            self.section['4'] = right

            self.is_set = True
        else:
            self.is_set = False
        return self.is_set


    def generate(self, simulation, sim_params, filter_params, saving=False, label_gui=None):
        '''
        generate simulation and filtered image
        params
        simulation: execute simulation (True or False)
        sim_params: simulator options
        filter_params: filter options - dictionary ('filtername': (True or False, min_value, max_value))

        if simulation - save 2 images
            1) simulation image
            2) filtered image - max 4 filters per one image
        else - save filtered image
        '''
        #print(simulation, sim_params, filter_params, saving)
        if not saving:
            img_num = 1
        else:
            img_num = sim_params[0] if sim_params else len(self.background_list)

        filter_list = self.get_filter_list(filter_params)
        img = None

        if saving:
            if simulation:
                root_dir_name = self.get_timestamp()
                img_dir, xml_dir, filter_dir = self.make_dir(root_dir_name, simulation=simulation)
            else:
                root_dir_name = self.background_path
                filter_dir = self.make_dir(root_dir_name)

        for i in range(img_num):
            if simulation:
                filename = '%05d' % i
                bg = random.choice(self.background_list)
                bg_img = Image.open(bg)
                section_list = list(self.section.keys())
                random.shuffle(section_list)
                img, box_list = self.generate_image(bg_img, sim_params[1:], section_list)

                if saving:
                    # save preprocessed image
                    #print(os.path.basename(img_dir))
                    self.save_image(img, dirname=img_dir, filename=filename + '.jpg')
                    # save xml
                    #print(filename)
                    self.save_xml(img_dir, filename, img.shape[:2], box_list, xml_dir)
            else:
                path = self.background_list[i]
                filename = os.path.basename(path).split('.')[0]
                img = cv2.imread(path)
            
            # apply filter
            filters = []
            if filter_list:
                for filter_index in range(len(filter_list)+1):
                    if filter_index < len(filter_list):
                        filters = filter_list[filter_index][0]
                        postfix = filter_list[filter_index][1]
                    else:
                        if len(filter_list) > 1:
                            filters = [filter for (filter, _) in filter_list]
                            postfix = 'all'
                    
                    img = self.apply_filters(img, filter_params, filters)
                    filtered_img_name = '{}_{}.jpg'.format(filename, postfix)
                    if saving:
                        # save filtered image
                        self.save_image(img, dirname=filter_dir, filename=filtered_img_name)

                        if simulation:
                            self.copy_xml(os.path.splitext(filtered_img_name)[0], xml_dir)

            if label_gui:
                label_gui.setText('%d / %d' % (i+1, img_num))
                label_gui.repaint()

        return img


    def set_bg_path(self, path):
        if path == '' or len(path) == 0:
            self.bg_ready = False
        else:
            self.background_path = os.path.dirname(path)
            self.background_list = self.get_file_list(path)
            self.bg_ready = True


    def set_png_path(self, path):
        if path == '' or len(path) == 0:
            self.png_ready = False
        else:
            self.png_path = os.path.dirname(path)
            self.png_list = self.get_file_list(path)
            self.png_ready = True


    def get_bg_path(self):
        return self.background_path


    def get_png_path(self):
        return self.png_path


    def select_background(self):
        #return cv2.imread(random.choice(self.background_list))
        return Image.open(random.choice(self.background_list))


    def select_png(self):
        #return cv2.imread(random.choice(self.png_list))
        return random.choice(self.png_list)


    def generate_image(self, bg, sim_params, section_list):
        completed = []

        num_object_range, scale_range, angle_range, max_iou, res = sim_params
        num_object = random.randint(num_object_range[0], num_object_range[1])
        rest = num_object
        n = 0
        start = True
        box_list = []

        for section_id in section_list:
            if start:
                n = random.randint(1, int(round(rest/2)+(rest%2)))
                start = False
            else:
                n = random.randint(0, rest)
            rest -= n
            section = self.section[str(section_id)]
            cnt = 0
            completed = []

            for i in range(0, n):
                not_intersect = []

                min_scale = float(scale_range[0]) if scale_range[0] != '' else 1.0
                max_scale = float(scale_range[1]) if scale_range[1] != '' else 1.0
                scale = random.uniform(min_scale, max_scale)

                min_angle = int(angle_range[0]) if angle_range[0] != '' else 0
                max_angle = int(angle_range[1]) if angle_range[1] != '' else 0
                angle = random.randint(min_angle, max_angle)

                png_file = self.select_png()
                png = Image.open(png_file)
                bw, bh = png.size

                if angle != 0:
                    png = png.rotate(angle, resample=Image.NEAREST)
                if scale != 1.0:
                    png = png.resize((int(bw * scale), int(bh * scale)))

                xc = random.randint(section[0], section[1])
                yc = random.randint(section[2], section[3])

                xmin = xc - int(bw / 2)
                ymin = yc - int(bh / 2)
                xmax = xmin + bw
                ymax = ymin + bh

                if completed:
                    for box in completed:
                        iou = self.get_iou(box, (xmin, ymin, xmax, ymax))
                        if iou < max_iou:
                            not_intersect.append(True)
                        else:
                            not_intersect.append(False)
                else:
                    not_intersect.append(True)
                
                if all(not_intersect):
                    bg.paste(png, (xmin, ymin), png)
                    completed.append((xmin, ymin, xmin+bw, ymin+bh))
                    png_name = os.path.splitext(os.path.basename(png_file))[0]
                    box_list.append((png_name, xmin, ymin, xmax, ymax))

                cnt += 1
            
            if rest == 0:
                break
        cv2_bg = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
        return cv2_bg, box_list


    def apply_filters(self, img, filter_params, filter):
        seq = iaa.Sequential(filter)
        filtered = seq(image=img)
        return filtered


    def get_file_list(self, path):
        return [os.path.join(path, fname) for fname in os.listdir(path) if 'jpg' in fname or 'png' in fname]


    def get_iou(self, box1, box2):
        # (xmin, ymin, xmax, ymax)
        x1 = max(box1[0], box2[0])
        x2 = min(box1[2], box2[2])
        y1 = max(box1[1], box2[1])
        y2 = min(box1[3], box2[3])

        intersection = (x2 - x1) * (y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = box1_area + box2_area - intersection

        iou = float(intersection / union)
        return iou


    def get_timestamp(self):
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    

    def make_dir(self, root_dir, simulation):
        img_dir = os.path.join(root_dir, self.IMG_DIR_NAME)
        xml_dir = os.path.join(root_dir, self.XML_DIR_NAME)
        filtered_dir = os.path.join(root_dir, self.FILTER_DIR_NAME)
        if not os.path.exists(root_dir):
            os.makedirs(filtered_dir)
        
        if simulation:
            os.makedirs(img_dir)
            os.makedirs(xml_dir)
            return (img_dir, xml_dir, filtered_dir)
        else:
            return filtered_dir
            

    def save_image(self, image, dirname = '', filename = ''):
        if not dirname or len(dirname) == 0:
            dirname = self.get_timestamp()
            self.make_dir(dirname)
        
        saved_path = os.path.join(dirname, filename)
        cv2.imwrite(saved_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        #print(saved_path + ' saved.')


    def save_xml(self, dirname, filename, imgsize, box_list, xml_dir):
        self.xml_generator.save_xml(dirname, filename, imgsize, box_list, xml_dir)


    def copy_xml(self, filename, xml_dir):
        org = filename.split('_')[0]
        self.xml_generator.copy_xml(org, filename, xml_dir)


    def ready(self):
        return self.bg_ready


    def get_filter_list(self, filter_params):
        filters = []
        br, cr, temp = filter_params.values()
        if br[0]:
            filters.append((iaa.AddToBrightness((br[1], br[2])), 'brightness'))
        if cr[0]:
            filters.append((iaa.LogContrast((float(cr[1]/10), float(cr[2]/10))), 'contrast'))
        if temp[0]:
            filters.append((iaa.ChangeColorTemperature(kelvin=(int(temp[1]), int(temp[2]))), 'kelvin'))
        return filters