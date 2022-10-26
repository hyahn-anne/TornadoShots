import sys
import os
import random
import cv2
import json
import configparser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from components.ui import *
from components.canvas import Canvas
from libs.simulator import Simulator


class Window(QWidget):
    OUTER_TAG = '0'
    INNER_TAG = '1'


    def __init__(self):
        super().__init__()
        self.outer_begin = QPoint()
        self.outer_end = QPoint()
        self.bg_path = ''
        self.png_path = ''
        self.simulator = Simulator()
        self.sample_img = None
        self.ow, self.oh = 0, 0
        self.num_of_images = 1
        self.is_set = False
        self.simulation_images = []
        self.filtered_images = []
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        self.filter_list = self.load_filter_list()
        self.sim_checked = False
        self.filter_index = []
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('TornadoShots')
        self.setGeometry(400, 200, 1700, 550)

        grid = QGridLayout()

        '''
        file layout
        '''
        grp_fileview = QGroupBox('Load Image')
        grp_fileview.setFixedWidth(630)
        v_fileview = QVBoxLayout()


        # file dialog layout
        h_filedialog = QHBoxLayout()
        self.btn_open = QPushButton('Open Dir')
        self.btn_open.clicked.connect(self.open_bg_dir)
        self.btn_open.setGeometry(10, 10, 200, 30)
        self.btn_open.setFixedHeight(30)

        self.edit_filepath = QTextEdit()
        self.edit_filepath.setFixedHeight(30)
        self.edit_filepath.setReadOnly(True)

        h_filedialog.addWidget(self.edit_filepath)
        h_filedialog.addWidget(self.btn_open)

        h_check_simulation = QHBoxLayout()
        self.chkbox_simulation = QCheckBox('Background Image')
        h_check_simulation.addWidget(self.chkbox_simulation)
        self.chkbox_simulation.setChecked(self.sim_checked)
        self.chkbox_simulation.stateChanged.connect(self.set_state)

        # image view layout
        h_fileview = QVBoxLayout()

        self.grp_filtered_img = QGroupBox('Preview')
        h_filtered_img = QHBoxLayout()
        h_filtered_img.setContentsMargins(0, 0, 0, 0)

        self.canvas = Canvas()
        h_filtered_img.addWidget(self.canvas)
        self.grp_filtered_img.setLayout(h_filtered_img)

        self.label_img_path = QLabel()
        self.label_img_path.setAlignment(Qt. AlignCenter)
        self.label_img_path.setFixedHeight(30)

        h_fileview.addWidget(self.grp_filtered_img)
        h_fileview.addWidget(self.label_img_path)
        h_fileview.addWidget(QLabel(''))

        v_fileview.addLayout(h_filedialog)
        v_fileview.addLayout(h_check_simulation)
        v_fileview.addLayout(h_fileview)
        grp_fileview.setLayout(v_fileview)

        # png list
        grp_png_list = QGroupBox('Load Foreground Image')
        grp_png_list.setFixedHeight(180)
        v_png_list = QVBoxLayout()

        h_png_dialog = QHBoxLayout()
        btn_png_open = QPushButton('Open Dir')
        btn_png_open.clicked.connect(self.open_png_dir)
        btn_png_open.setGeometry(10, 10, 100, 40)
        btn_png_open.setFixedWidth(100)
        btn_png_open.setFixedHeight(30)

        self.edit_png_path = QTextEdit()
        self.edit_png_path.setFixedWidth(500)
        self.edit_png_path.setFixedHeight(30)
        self.edit_png_path.setReadOnly(True)

        h_png_dialog.addWidget(self.edit_png_path)
        h_png_dialog.addWidget(btn_png_open)

        h_png_list = QHBoxLayout()
        self.list_widget = QListWidget()
        self.model = QStandardItemModel()
        self.list_widget.setFixedWidth(500)
        self.list_widget.setFixedHeight(100)
        self.png_label = QLabel()
        self.png_label.setFixedWidth(100)
        h_png_list.addWidget(self.list_widget)
        h_png_list.addWidget(self.png_label)

        self.list_widget.itemSelectionChanged.connect(self.select_item)

        v_png_list.addLayout(h_png_dialog)
        v_png_list.addLayout(h_png_list)
        grp_png_list.setLayout(v_png_list)


        '''
        simulation layout
        '''
        grp_simview = QGroupBox('Simulation Setup')
        grp_simview.setFixedWidth(550)
        v_simview = QVBoxLayout()

        # select area
        grp_set_area = QGroupBox('Set Area')
        grp_set_area.setFixedHeight(130)
        v_area = QVBoxLayout()

        outer_rect_area = RectArea()
        h_outer_area = outer_rect_area.create_area('Outer')
        btn_outer = h_outer_area.itemAt(1).widget()
        label_outer_area = h_outer_area.itemAt(h_outer_area.count()-1).widget()
        btn_outer_reset = h_outer_area.itemAt(2).widget()

        btn_outer.clicked.connect(lambda: self.set_drawing_mode(label_outer_area, self.OUTER_TAG))
        btn_outer_reset.clicked.connect(lambda: self.reset(label_outer_area, self.OUTER_TAG))

        inner_rect_area = RectArea()
        h_inner_area = inner_rect_area.create_area('Inner')
        btn_inner = h_inner_area.itemAt(1).widget()
        label_inner_area = h_inner_area.itemAt(h_inner_area.count()-1).widget()
        btn_inner_reset = h_inner_area.itemAt(2).widget()

        btn_inner.clicked.connect(lambda: self.set_drawing_mode(label_inner_area, self.INNER_TAG))
        btn_inner_reset.clicked.connect(lambda: self.reset(label_inner_area, self.INNER_TAG))

        h_btn_area = QHBoxLayout()
        h_btn_area.addStretch(1)
        btn_apply_area = QPushButton('Apply')
        h_btn_area.addWidget(btn_apply_area)
        btn_apply_area.clicked.connect(self.apply_area)

        v_area.addLayout(h_outer_area)
        v_area.addLayout(h_inner_area)
        v_area.addLayout(h_btn_area)
        grp_set_area.setLayout(v_area)


        # simulation settings
        grp_num_object = QGroupBox('Number of objects')
        grp_num_object.setFixedHeight(80)
        self.object_num_tb = TextBox()
        h_max_num = self.object_num_tb.create_textbox_panel()
        grp_num_object.setLayout(h_max_num)

        grp_png_scale = QGroupBox('PNG Scale')
        grp_png_scale.setFixedHeight(80)
        self.scale_tb = TextBox()
        h_scale = self.scale_tb.create_textbox_panel()
        grp_png_scale.setLayout(h_scale)

        grp_rotation = QGroupBox('Rotation')
        grp_rotation.setFixedHeight(80)
        self.rotation_tb = TextBox()
        h_rotation = self.rotation_tb.create_textbox_panel()
        grp_rotation.setLayout(h_rotation)

        grp_iou_res = QGroupBox('iou, resolution')
        grp_iou_res.setFixedHeight(80)
        self.iou_res_tb = TextBox()
        h_iou_res = self.iou_res_tb.create_textbox_panel(label1='iou', label2='width')
        grp_iou_res.setLayout(h_iou_res)

        h_buttons = QHBoxLayout()
        self.edit_num_img = QTextEdit()
        self.edit_num_img.setFixedWidth(80)
        self.edit_num_img.setFixedHeight(27)

        self.chk_trainset = QCheckBox('Use train / validation set')

        h_buttons.addWidget(QLabel('num of images'))
        h_buttons.addWidget(self.edit_num_img)
        h_buttons.addWidget(self.chk_trainset)
        h_buttons.addStretch()

        v_simview.addWidget(grp_set_area)
        v_simview.addWidget(grp_png_list)
        v_simview.addWidget(grp_num_object)
        v_simview.addWidget(grp_png_scale)
        v_simview.addWidget(grp_rotation)
        v_simview.addWidget(grp_iou_res)
        v_simview.addLayout(h_buttons)
        grp_simview.setLayout(v_simview)
        

        '''
        augmentation layout
        '''
        # filter layout
        grp_filterview = QGroupBox('Filter List')
        grp_filterview.setFixedWidth(500)
        #grp_filterview.setFixedHeight(200)
        v_filterview = QVBoxLayout()


        # filter list combo box
        grp_filter = QGroupBox('Predefined Filters')
        grp_filter.setFixedHeight(80)
        h_filterlist = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedHeight(30)
        self.filter_combo.addItem('--- Select Filter ---')
        for i, filter in enumerate(self.filter_list):
            filter_name = filter['name']
            self.filter_combo.addItem(filter_name)
        h_filterlist.addWidget(self.filter_combo)
        grp_filter.setLayout(h_filterlist)
        self.filter_combo.currentIndexChanged.connect(self.set_filters)


        # brightness filter
        v_br = QVBoxLayout()
        self.br_chkbox = QCheckBox('Brightness')
        grp_brightness = QGroupBox()
        v_br_slider = QVBoxLayout()
        self.br_min_slider = Slider()
        h_br_min_slider = self.br_min_slider.create_slide_panel('Min', -10, 10)
        self.br_max_slider = Slider()
        h_br_max_slider = self.br_max_slider.create_slide_panel('Max', -10, 10)
        v_br_slider.addLayout(h_br_min_slider)
        v_br_slider.addLayout(h_br_max_slider)
        grp_brightness.setLayout(v_br_slider)
        v_br.addWidget(self.br_chkbox)
        v_br.addWidget(grp_brightness)

        # contrast filter
        v_cr = QVBoxLayout()
        self.cr_chkbox = QCheckBox('Contrast')
        grp_contrast = QGroupBox()
        v_cr_slider = QVBoxLayout()
        self.cr_min_slider = Slider(is_float=True)
        h_cr_min_slider = self.cr_min_slider.create_slide_panel('Min', 4, 16)
        self.cr_max_slider = Slider(is_float=True)
        h_cr_max_slider = self.cr_max_slider.create_slide_panel('Max', 4, 16)
        v_cr_slider.addLayout(h_cr_min_slider)
        v_cr_slider.addLayout(h_cr_max_slider)
        grp_contrast.setLayout(v_cr_slider)
        v_cr.addWidget(self.cr_chkbox)
        v_cr.addWidget(grp_contrast)


        # contrast temperature
        v_temp = QVBoxLayout()
        self.temp_chkbox = QCheckBox('Temperature')
        grp_temp = QGroupBox()
        grp_temp.setFixedHeight(60)
        v_temp_slider = QVBoxLayout()
        self.temp_tb = TextBox()
        h_temperature = self.temp_tb.create_textbox_panel(label1='min', label2='max')
        v_temp_slider.addLayout(h_temperature)
        grp_temp.setLayout(v_temp_slider)
        v_temp.addWidget(self.temp_chkbox)
        v_temp.addWidget(grp_temp)

        h_filter_buttons = QHBoxLayout()
        self.btn_apply = QPushButton('Apply')
        self.btn_apply.setFixedHeight(27)
        self.btn_filter_preview = QPushButton('Preview')
        self.btn_filter_preview.setFixedHeight(27)
        self.label_iteration = QLabel('0 / 0')
        self.label_iteration.setFixedWidth(200)
        self.label_iteration.setFixedHeight(30)
    
        h_filter_buttons.addWidget(self.label_iteration)
        h_filter_buttons.addWidget(self.btn_filter_preview)
        h_filter_buttons.addWidget(self.btn_apply)

        self.btn_apply.clicked.connect(lambda: self.generate(btn='gen'))
        self.btn_filter_preview.clicked.connect(lambda: self.generate(btn='preview'))

        # build filter view
        v_filterview.addWidget(grp_filter)
        v_filterview.addLayout(v_br)
        v_filterview.addLayout(v_cr)
        v_filterview.addLayout(v_temp)
        v_filterview.addLayout(h_filter_buttons)
        grp_filterview.setLayout(v_filterview)


        '''
        Set Grid Layout
        '''
        # build grid layout
        grid.addWidget(grp_fileview, 0, 0)
        grid.addWidget(grp_png_list, 1, 0)
        grid.addWidget(grp_simview, 0, 1, 2, 1)
        grid.addWidget(grp_filterview, 0, 2, 2, 1)
        self.setLayout(grid)

        self.init_value()

        self.show()


    def open_bg_dir(self):
        dir_path = QFileDialog.getExistingDirectory(None, 'Select a folder')
        self.simulator.set_bg_path(dir_path)
        flist = []
        if dir_path:
            flist = os.listdir(dir_path)
            flist = [f for f in flist if not os.path.isdir(f) and (f.split('.')[-1] == 'jpg' or f.split('.')[-1] == 'png')]
        
        if len(flist) > 0:
            f = random.choice(flist)
            self.edit_filepath.setText(dir_path)
            img_name = os.path.join(dir_path, f)
            self.bg_path = img_name
            img = cv2.imread(img_name)
            self.oh, self.ow = img.shape[:2]
            self.set_image(img)
            self.label_iteration.setText('0 / %d' % len(flist))
            self.iou_res_tb.set_resolution(self.ow)


    def open_png_dir(self):
        if self.list_widget.count() > 0:
            self.list_widget.clear()

        dir_path = QFileDialog.getExistingDirectory(None, 'Select a folder')
        flist = []
        if dir_path:
            self.simulator.set_png_path(dir_path)
            self.png_path = dir_path
            self.edit_png_path.setText(dir_path)
            flist = os.listdir(dir_path)
            flist = [f for f in flist if f.split('.')[-1] == 'jpg' or f.split('.')[-1] == 'png']

        for f in flist:
            self.list_widget.addItem(f)


    def set_drawing_mode(self, label_widget, tag):
        self.canvas.set_drawing_mode(True)
        self.canvas.override_cursor(Qt.CrossCursor)
        self.canvas.set_label(label_widget)
        self.canvas.set_tag(tag)
    

    def set_image(self, img, img_name='preview'):
        self.canvas.clear()
        h, w = img.shape[:2]
        wr = float(int(self.config['PREVIEW']['WIDTH']) / w)
        hr = float(int(self.config['PREVIEW']['HEIGHT']) / h)
        h = int(h * hr)
        w = int(w * wr)
        img = cv2.resize(img, (w, h), cv2.INTER_AREA)
        self.sample_img = img.copy()
        qimg = QImage(img.data, w, h, QImage.Format_RGB888).rgbSwapped()
        self.canvas.setPixmap(QPixmap.fromImage(qimg))
        self.grp_filtered_img.setFixedWidth(w)
        self.grp_filtered_img.adjustSize()
        self.label_img_path.setText(img_name)


    def reset(self, label_widget, tag):
        self.canvas.reset(label_widget, tag)


    def load_filter_list(self):
        f = open(self.config['FILTER']['FILTER_FILENAME'])
        json_filter_list = json.load(f)
        filter_list = json_filter_list['filters']
        #filter_list.insert(0, '--- Select Filter ---')
        return filter_list


    def set_filters(self):
        filter_index = self.filter_combo.currentIndex()
        if filter_index == 0:
            self.reset_slider()
        else:
            filter = self.filter_list[filter_index-1]
            br = int(filter['brightness'])
            cr = int(float(filter['contrast']) * 10)
            temp = int(filter['temperature'])
            self.set_filter_value(br, cr, temp)


    def select_item(self):
        png_name = [item.text() for item in self.list_widget.selectedItems()][0]
        png_path = os.path.join(self.png_path, png_name)
        img = cv2.imread(png_path)
        h, w = img.shape[:2]
        hr = float(100 / h)
        wr = float(100 / w)
        h = int(h * hr)
        w = int(w * wr)
        resized = cv2.resize(img, (w, h), cv2.INTER_AREA)
        qimg = QImage(resized.data, w, h, QImage.Format_RGB888).rgbSwapped()
        self.png_label.setPixmap(QPixmap.fromImage(qimg))


    def apply_area(self):
        rectangles = self.canvas.get_rects()

        if len(rectangles) > 0:
            h, w = self.sample_img.shape[:2]
            rw = float(w / self.ow)
            rh = float(h / self.oh)

            d = {}

            if len(rectangles) < 2:
                QMessageBox.information(self, 'Alert', 'Not enough rectangles')
            else:
                for rect in rectangles:
                    r, label  = rect
                    xmin, ymin, bw, bh = r
                    xmax = xmin + bw
                    ymax = ymin + bh

                    xmin = int(round(xmin / rw))
                    ymin = int(round(ymin / rh))
                    xmax = int(round(xmax / rw))
                    ymax = int(round(ymax / rh))

                    r = (xmin, ymin, xmax, ymax)
                    d[label] = r
            self.is_set = self.simulator.divide(d)
            if self.is_set:
                QMessageBox.information(self, 'Confirm', 'Saved!')
        else:
            QMessageBox.information(self, 'Error', 'no area')
            self.is_set = False


    def reset_slider(self):
        self.br_min_slider.set_value(int(self.config['FILTER']['BRIGHTNESS']))
        self.br_max_slider.set_value(int(self.config['FILTER']['BRIGHTNESS']))
        self.cr_min_slider.set_value(int(self.config['FILTER']['CONTRAST']))
        self.cr_max_slider.set_value(int(self.config['FILTER']['CONTRAST']))
        self.temp_tb.set_text(self.config['FILTER']['MIN_KELVIN'], self.config['FILTER']['MAX_KELVIN'])
        self.br_chkbox.setChecked(False)
        self.cr_chkbox.setChecked(False)
        self.temp_chkbox.setChecked(False)


    def set_filter_value(self, br, cr, temp):
        self.br_min_slider.set_value(br)
        self.br_max_slider.set_value(br)
        self.cr_min_slider.set_value(cr)
        self.cr_max_slider.set_value(cr)
        self.temp_tb.set_text(temp, temp)
        self.br_chkbox.setChecked(True)
        self.cr_chkbox.setChecked(True)
        self.temp_chkbox.setChecked(True)


    def generate(self, btn='gen'):
        filter_params = self.get_filter_params()
        sim_params = ()
        saving = False

        # sim param check
        if self.sim_checked:
            sim_params = self.get_simulator_params(btn)
            if not self.png_path:
                QMessageBox.information(self, 'Error', 'No Foreground Images')
                return
            if not self.is_set:
                QMessageBox.information(self, 'Error', 'No Area')
                return
            if '' in sim_params:
                QMessageBox.information(self, 'Error', 'Empty Params')
                return
        
        # temperatur check
        if self.temp_chkbox.isChecked():
            if '' in filter_params['temp']:
                QMessageBox.information(self, 'Error', 'No Temperature')
                return
            else:
                temp = tuple(map(int, self.temp_tb.get_text()))

                if temp[0] < 1000 or temp[1] > 10000:
                    QMessageBox.information(self, 'Error', 'Temperature range: 1000~10000')
                    return
        
        if self.bg_path:
            if btn == 'gen':
                self.label_iteration.setText('0 / %s' % self.edit_num_img.toPlainText())
                self.label_iteration.repaint()
                self.btn_apply.setEnabled(False)
                saving = True
                label_gui = self.label_iteration
            else:
                label_gui = None
                saving = False

            preview = self.simulator.generate(self.sim_checked, sim_params, filter_params, saving=saving, label_gui=label_gui)

            if preview.size != 0:
                self.set_image(preview)

            self.btn_apply.setEnabled(True)
            self.btn_apply.repaint()
        else:
            QMessageBox.information(self, 'Error', 'No Background Images')


    def save_images(self):
        if self.simulation_images:
            self.simulator.save(self.simulation_images)
            self.btn_save.setEnabled(False)
            QMessageBox.information(self, 'Saved!', 'Image Saved!')
        else:
            QMessageBox.information(self, 'Error', 'No images')


    def init_value(self):
        self.object_num_tb.set_text(self.config['SIMULATOR']['MIN_OBJECT_NUM'], self.config['SIMULATOR']['MAX_OBJECT_NUM'])
        self.scale_tb.set_text(self.config['SIMULATOR']['DEFAULT_SCALE'], self.config['SIMULATOR']['DEFAULT_SCALE'])
        self.rotation_tb.set_text(self.config['SIMULATOR']['MIN_ANGLE'], self.config['SIMULATOR']['MAX_ANGLE'])
        self.iou_res_tb.set_text(self.config['SIMULATOR']['DEFAULT_IOU'], '')
        self.edit_num_img.setText(self.config['SIMULATOR']['DEFAULT_IMG_NUM'])
        self.temp_tb.set_text(self.config['FILTER']['MIN_KELVIN'], self.config['FILTER']['MAX_KELVIN'])


    def set_state(self):
        if self.sim_checked:
            self.sim_checked = False
        else:
            self.sim_checked = True


    def get_simulator_params(self, btn):
        #num_img, num, scale, angle, iou, res
        num_img = int(self.edit_num_img.toPlainText()) if btn == 'gen' else 1
        num_obj = tuple(map(int, self.object_num_tb.get_text()))
        scale = tuple(map(float, self.scale_tb.get_text()))
        angle = tuple(map(int, self.rotation_tb.get_text()))
        iou, res = self.iou_res_tb.get_text()
        return (num_img, num_obj, scale, angle, float(iou), int(res))


    def get_filter_params(self):
        #br, cr, temperature, image_list
        br = (self.br_chkbox.isChecked(), int(self.br_min_slider.get_value()), int(self.br_max_slider.get_value()))
        cr = (self.cr_chkbox.isChecked(), float(self.cr_min_slider.get_value()), float(self.cr_max_slider.get_value()))
        kelvin_min, kelvin_max = self.temp_tb.get_text()
        temp = (self.temp_chkbox.isChecked(), kelvin_min, kelvin_max)
        return {'br': br, 'cr': cr, 'temp': temp}