# -*- coding: utf-8 -*-

import sys
import main_window
import preview_window
import pop_window
from cvvc_reclist_generator import ReclistGenerator
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from collections import UserDict


class Param(UserDict):
    def __init__(self):
        super(Param, self).__init__()
        self.dict_path = ""
        self.length = 6
        self.plan_b = False
        self.group = True
        self.sep = False
        self.cv_head = True
        self.random = False
        self.stop_coda = None
        self.bpm = 120
        self.beat = 4
        self.max_cv = 1
        self.max_vc = 1
        self.max_vr = 1
        self.output_path = ".\\"
        self.reclist = None
        self.oto = None
        self.reclist_name = "reclist.txt"
        self.oto_name = "oto.ini"

    def get_reclist_param(self):
        param = {"length": self.length, "plan_b": self.plan_b, "group": self.group,
                 "cv_head": self.cv_head, "sep": self.sep, "random": self.random,
                 "stop_coda": self.stop_coda}
        return param

    def get_oto_param(self):
        param = {"length": self.length, "plan_b": self.plan_b, "cv_head": self.cv_head,
                 "stop_coda": self.stop_coda, "bpm": self.bpm,
                 "max_cv": self.max_cv, "max_vc": self.max_vc, "max_vr": self.max_vr}
        return param

    def get_output_param(self):
        param = {"output_path": self.output_path,
                 "reclist_name": self.reclist_name,
                 "oto_name": self.oto_name}
        return param


class MainWindow(QMainWindow, main_window.Ui_Form):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("cvvc generator by cc")
        self.output_path_linedit.setText("./")

        self.dict_path_open_button.clicked.connect(self.choose_dictfile)
        self.stop_coda_preset_button.clicked.connect(self.open_stop_coda_preset)
        self.output_path_open_button.clicked.connect(self.choose_output_path)
        self.preview_botton.clicked.connect(self.preview)
        self.gen_button.clicked.connect(self.gen_files)

    def choose_dictfile(self):
        dict_path_tuple = QFileDialog.getOpenFileNames(self, "选择字典文件",
                                                       "./", "文本文件 (*.txt)")
        try:
            dict_path = dict_path_tuple[0][0]
            self.dict_path_linedit.setText(dict_path)
            global global_param
            global_param.dict_path = dict_path
        except IndexError:
            pass

    def open_stop_coda_preset(self):
        preset_path_tuple = QFileDialog.getOpenFileNames(self, "选择预设文件",
                                                         "./", "文本文件 (*.txt)")
        try:
            preset = preset_path_tuple[0][0]
            preset.encode("unicode-escape").decode()
            with open(preset, mode="r") as f:
                stop_coda_str = f.read()
            stop_coda_list = []
            for line in stop_coda_str.splitlines():
                line.strip()
                for stop_coda in line.split(sep=","):
                    if stop_coda != "":
                        stop_coda_list.append(stop_coda)
            global global_param
            global_param.stop_coda = set(stop_coda_list)
            stop_coda_str = ",".join(stop_coda_list)
            self.stop_coda_linedit.setText(stop_coda_str)
        except IndexError:
            pass

    def choose_output_path(self):
        output_path = QFileDialog.getExistingDirectory(self, "选择保存位置",
                                                        "./")
        try:
            self.output_path_linedit.setText(output_path)
            global global_param
            global_param.output_path = output_path
        except IndexError:
            pass

    def check_and_gen(self):
        global global_param
        if global_param.dict_path == "":
            self.warning_window = WarningWindow("你没有选择字典文件诶！")
            self.warning_window.show()
            return True
        try:
            self.generate()
        except FileNotFoundError:
            self.warning_window = WarningWindow("字典文件名是不是包含非英文字符？"
                                                "麻烦你先修改为全英文件名啦~")
            self.warning_window.show()
            return True
        except IndexError:
            self.warning_window = WarningWindow("你选择的字典文件好像有格式错误哦，"
                                                "建议好好检查一下呢！")
            self.warning_window.show()
            return True
        except Exception:
            self.warning_window = WarningWindow("是奇怪的错误出现了，"
                                                "这边是建议联系一下开发者呢……")
            self.warning_window.show()
            return True

    def preview(self):
        if self.check_and_gen():
            return
        self.preview_window = PreviewWindow()
        self.preview_window.show()

    def generate(self):
        global global_param
        self.get_param()
        reclist_param = global_param.get_reclist_param()
        oto_param = global_param.get_oto_param()
        generator = ReclistGenerator()
        generator.read_dict(global_param.dict_path)
        generator.gen_cvvc_reclist(**reclist_param)
        generator.gen_oto(**oto_param)
        global_param.reclist = generator.reclist.copy()
        global_param.oto = generator.oto.copy()

    def get_param(self):
        global global_param
        global_param.length = self.length_spinbox.value()
        global_param.plan_b = self.plan_b_checkbox.isChecked()
        global_param.group = self.group_checkbox.isChecked()
        global_param.sep = self.sep_checkbox.isChecked()
        global_param.cv_head = self.cv_head_checkbox.isChecked()
        global_param.random = self.random_checkbox.isChecked()
        for stop_coda in self.stop_coda_linedit.text().split(","):
            if stop_coda != "":
                global_param.stop_coda.add(stop_coda)
        global_param.bpm = self.bpm_spin_box.value()
        global_param.beat = self.beat_spinbox.value()
        global_param.max_cv = self.max_cv_spinbox.value()
        global_param.max_vc = self.max_vc_spinbox.value()
        global_param.max_vr = self.max_vr_spinbox.value()
        global_param.reclist_name = self.reclist_name_linedit.text()
        global_param.oto_name = self.oto_name_linedit.text()

    def gen_files(self):
        self.check_and_gen()
        global global_param

        reclist_str = ""
        for row in global_param.reclist:
            for cvv in row:
                reclist_str += "_%s" % cvv.cvv
            reclist_str += "\n"
        oto_str = ""
        for part in global_param.oto:
            for oto in part:
                oto_str += "%s\n" % oto

        reclist_path = global_param.output_path + "/" + global_param.reclist_name
        oto_path = global_param.output_path + "/" +global_param.oto_name
        with open(reclist_path, mode="w+") as f:
            f.write(reclist_str)
        with open(oto_path, mode="w+") as f:
            f.write(oto_str)

        self.pop_window = SuccessWindow("录音表和oto已经生成完毕并输出到指定路径了！")
        self.pop_window.show()


class PreviewWindow(QMainWindow, preview_window.Ui_Form):
    def __init__(self, parent=None):
        super(PreviewWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Preview")
        global global_param
        reclist_num = len(global_param.reclist)
        oto_num = 0
        for part in global_param.oto:
            oto_num += len(part)
        self.info_label.setText("总行数：{}， 总oto数：{}".format(reclist_num, oto_num))
        self.show_list()
        self.pushButton_2.clicked.connect(self.gen_files)


    def show_list(self):
        global global_param
        reclist_str = ""
        for row in global_param.reclist:
            for cvv in row:
                reclist_str += "_{}".format(cvv.cvv)
            reclist_str += "\n"
        self.reclist_textbrowser.setText(reclist_str)

        oto_str = ""
        for oto_part in global_param.oto:
            for oto in oto_part:
                oto_str += "{}\n".format(oto)
        self.oto_textbrowser.setText(oto_str)

    def gen_files(self):
        global global_param

        reclist_str = ""
        for row in global_param.reclist:
            for cvv in row:
                reclist_str += "_%s" % cvv.cvv
            reclist_str += "\n"
        oto_str = ""
        for part in global_param.oto:
            for oto in part:
                oto_str += "%s\n" % oto

        reclist_path = global_param.output_path + "/" + global_param.reclist_name
        oto_path = global_param.output_path + "/" + global_param.oto_name
        with open(reclist_path, mode="w+") as f:
            f.write(reclist_str)
        with open(oto_path, mode="w+") as f:
            f.write(oto_str)

        self.pop_window = SuccessWindow("录音表和oto已经生成完毕并输出到指定路径了！")
        self.pop_window.show()
        self.close()


class WarningWindow(QMainWindow, pop_window.Ui_Form):
    def __init__(self, info: str):
        super(WarningWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Warning!")
        self.title_label.setText("ERROR 啦ヽ(　>д<)ノ")
        self.detail_label.setText("错误信息：" + info)


class SuccessWindow(QMainWindow, pop_window.Ui_Form):
    def __init__(self, info: str):
        super(SuccessWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Output Success!")
        self.title_label.setText("吐表惹成功惹(～￣▽￣)～ ")
        self.detail_label.setText(info)


if __name__ == "__main__":
    global_param = Param()
    app = QApplication(sys.argv)
    myWin = MainWindow()
    myWin.show()
    sys.exit(app.exec_())
