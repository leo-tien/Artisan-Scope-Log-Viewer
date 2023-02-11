# -*- coding: utf-8 -*-
__version__ = "1.0.0"

import os, errno, json
from os import environ

if "ANDROID_BOOTLOGO" in environ:
    print("Viewer On Android Environment")
    if not "PYDROID3_LICENSE" in environ:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    base = "/sdcard/aslviewer"
else:
    base = "/tmp/aslviewer"

if not os.path.exists(base):
    try:
        os.makedirs(base, exist_ok=True)
        print("Database directory created.")
    except OSError as e:
        print("Cannot create {}.".format(base))
        if e.errno != errno.EEXIST:
            raise

os.environ["KIVY_HOME"] = base

import kivy
from kivy.config import Config

Config.set("kivy", "log_level", "debug")
Config.set("kivy", "default_font", ["Arial Unicode MS", "fonts/arial-unicode-ms.ttf"])

from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button

from garden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np

Builder.load_string('''
<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            path: "/sdcard"

        BoxLayout:
            size_hint_y: None
            height: 35
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<ViewerWidget>:
    #:set AirForceBlue 0, 0.19, 0.56, 1
    #:set Black 0, 0, 0, 1
    #:set DarkGray 0.35, 0.35, 0.35, 1
    #:set Gray 0.6, 0.6, 0, 1
    #:set Red 1, 0, 0, 1
    #:set SkyBlue 0.47, 0.71, 1, 1
    #:set White 1, 1, 1, 1
    BoxLayout:
        orientation: "horizontal"
        canvas.before:
            Color:
                rgba: Black
            Rectangle:
                pos: self.pos
                size: self.size
        padding: 5
        BoxLayout:
            orientation: "vertical"
            id: fig
            spacing: 2
            padding: 2
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: DarkGray
                Line:
                    rounded_rectangle: self.x, self.y, self.width, self.height, 10
                    width: 2
            size_hint: (0.1, 1)
            padding: self.width / 5
            spacing: 20
            Button:
                id: btn_load
                size_hint_x: None
                size_hint_y: None
                width: self.parent.width / 5 * 3
                height: self.width
                halign: "center"
                valign: "middle"
                text: "+"
                font_size: 0.65 * self.height
                on_release: root.show_load_dialog()
            Button:
                id: btn_remove
                size_hint_x: None
                size_hint_y: None
                width: self.parent.width / 5 * 3
                height: self.width
                halign: "center"
                valign: "middle"
                text: "-"
                font_size: 0.65 * self.height
                on_release: root.remove_child_figure()
            Label:
                id: label_notes
                size_hint_y: None
                width: self.parent.width / 5 * 3
                height: self.width
            ScrollView:
                do_scroll_x: True
                do_scroll_y: True
                BoxLayout:
                    orientation: "vertical"
                    id: scroll_notes
                    size_hint_y: None
                    height: 300
''')

nof = 0
notes_popup = []
notes_button = []

class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ViewerWidget(BoxLayout):
    def remove_child_figure(self):
        if len(self.ids.fig.children) > 0:
            self.ids.fig.remove_widget(self.ids.fig.children[0])
        if len(self.ids.scroll_notes.children) > 0:
            self.ids.scroll_notes.remove_widget(self.ids.scroll_notes.children[0])
        global nof
        global notes_popup
        global notes_button
        del notes_popup[nof-1]
        del notes_button[nof-1]
        nof -= 1
        print("Remove:\nnof=%s\nlen(notes_popup)=%s\nlen(notes_button)=%s"%(nof, len(notes_popup), len(notes_button)))

    def draw(self, mode, beans, weight, roastisodate, timex, temp1, temp2, extratimex, extratemp1, phases, zmin, zmax, xmin, xmax, ymin, ymax, computed, anno):
        plt.plot(timex, temp2, "k-") # BT
        new_xmin = int(xmin//60)
        new_xmax = int(xmax//60)
        new_xticks = np.linspace(xmin, xmax, new_xmax - new_xmin + 1)
        plt.xticks(new_xticks)
        plt.ylim([ymin, ymax])
        plt.yticks(np.linspace(ymin, ymax, 11))
        plt.ylabel(mode)

        plt.plot(timex, temp1, "r-") # ET
        plt.plot(extratimex, extratemp1, "b-") # ROR
        self.ids.fig.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        print("test ror")

    def draw2(self, mode, beans, weight, roastisodate, timex, temp1, temp2, extratimex, extratemp1, phases, zmin, zmax, xmin, xmax, ymin, ymax, computed, anno):
        font_prop = fm.FontProperties(fname="fonts/arial-unicode-ms.ttf", size = 18)
        plt.rcParams["figure.constrained_layout.use"] = True
        # Set the default text font size
        plt.rc('font', size=14)
        # Set the axes title font size
        plt.rc('axes', titlesize=14)
        # Set the axes labels font size
        plt.rc('axes', labelsize=14)
        # Set the font size for x tick labels
        plt.rc('xtick', labelsize=14)
        # Set the font size for y tick labels
        plt.rc('ytick', labelsize=14)
        # Set the legend font size
        plt.rc('legend', fontsize=12)
        # Set the font size of the figure title
        plt.rc('figure', titlesize=18)

        ax1 = plt.figure().add_subplot(111)
        ax1.plot(timex, temp2, "k-", label="BT") # BT
        ax1.plot(timex, temp1, "r-", label="ET") # ET

        ax2 = ax1.twinx()
        ax2.plot(extratimex, extratemp1, "b-", label="ROR") # ROR

        global nof
        title_text = str(nof) + ". " + roastisodate
        if len(beans) > 0:
            title_text += " " + beans
        unit = weight[2]
        w_in = computed["weightin"]
        w_out = computed["weightout"]
        if w_in > 0:
            title_text += " " + str(w_in) + unit
        if w_out > 0:
            title_text += " -> " + str(w_out) + unit
        try:
            w_loss = str(computed["weight_loss"])
            title_text += " -" + w_loss + "%"
        except KeyError:
            w_loss = ""
            pass

        plt.title(title_text, fontproperties=font_prop)

        ax1.legend(loc="lower left")
        ax2.legend(loc="lower right")

        ax1.grid(color = "grey", linestyle = "-.", linewidth = 0.5)

        ax1.set_xlabel("min")
        ax1.set_ylabel(mode, rotation=0)
        ax2.set_ylabel(mode + "/min")

        ax2.set_ylim(zmin, zmax)
        ax1.set_yticks(np.linspace(ymin, ymax, 11))
        ax1.set_ylim(ymin, ymax)
        new_xmin = int(xmin//60)
        new_xmax = int(xmax//60)
        new_xticks = (np.linspace(xmin, xmax, new_xmax - new_xmin + 1)//60).astype(int)
        ax1.set_xticks(new_xticks*60)
        ax1.set_xticklabels(new_xticks)

        anno_fsize = 12
        # anno CHARGE
        ax1.annotate("CHARGE " + str(int(computed["CHARGE_BT"])),
                xy=(0, computed["CHARGE_BT"]),
                xytext=(anno[0][3], anno[0][4]),
                arrowprops={
                    "width":1,
                    "headlength":8,
                    "headwidth":10,
                    "facecolor":"#000",
                    "shrink":0.05},
                fontsize=anno_fsize)

        # anno TP
        tp_time = "%s:%s"%(int(computed["TP_time"]//60), int(computed["TP_time"]%60))
        ax1.annotate("TP " + tp_time + " " + str(int(computed["TP_BT"])),
                xy=(computed["TP_time"], computed["TP_BT"]),
                xytext=(anno[1][3], anno[1][4]),
                arrowprops={
                    "width":1,
                    "headlength":8,
                    "headwidth":10,
                    "facecolor":"#000",
                    "shrink":0.05},
                fontsize=anno_fsize)

        # anno DE
        de_time = "%s:%s"%(int(computed["DRY_time"]//60), int(computed["DRY_time"]%60))
        ax1.annotate("DE " + de_time + " " + str(int(computed["DRY_BT"])),
                xy=(computed["DRY_time"], computed["DRY_BT"]),
                xytext=(anno[2][3], anno[2][4]),
                arrowprops={
                    "width":1,
                    "headlength":8,
                    "headwidth":10,
                    "facecolor":"#000",
                    "shrink":0.05},
                fontsize=anno_fsize)

        # anno FC
        fc_time = "%s:%s"%(int(computed["FCs_time"]//60), int(computed["FCs_time"]%60))
        ax1.annotate("FCs " + fc_time + " " + str(int(computed["FCs_BT"])),
                xy=(computed["FCs_time"], computed["FCs_BT"]),
                xytext=(anno[3][3], anno[3][4]),
                arrowprops={
                    "width":1,
                    "headlength":8,
                    "headwidth":10,
                    "facecolor":"#000",
                    "shrink":0.05},
                fontsize=anno_fsize)

        # anno DROP
        try:
            drop_time = "%s:%s"%(int(computed["DROP_time"]//60), int(computed["DROP_time"]%60))
            ax1.annotate("DROP " + drop_time + " " + str(int(computed["DROP_BT"])),
                    xy=(computed["DROP_time"], computed["DROP_BT"]),
                    xytext=(anno[4][3], anno[4][4]),
                    arrowprops={
                        "width":1,
                        "headlength":8,
                        "headwidth":10,
                        "facecolor":"#000",
                        "shrink":0.05},
                    fontsize=anno_fsize)
        except KeyError:
            pass

        # color of phases
        dry_phase_color = (0, 0.5, 0)
        mid_phase_color = (1, 0.65, 0)
        fin_phase_color = (0.6, 0.4, 0.2)
        ax1.axhspan(phases[0], phases[1], facecolor=dry_phase_color, alpha=0.3)
        ax1.axhspan(phases[1], phases[2], facecolor=mid_phase_color, alpha=0.3)
        ax1.axhspan(phases[2], phases[3], facecolor=fin_phase_color, alpha=0.3)
        try:
            plt.axvspan(computed["FCs_time"], computed["DROP_time"], facecolor=(1, 1, 0), alpha=0.3)
        except KeyError:
            pass

        try:
            # phases bar
            dryphasetime = computed["dryphasetime"]
            midphasetime = computed["midphasetime"]
            finishphasetime = computed["finishphasetime"]
            totaltime = computed["totaltime"]
            patch_x1 = 0
            patch_x2 = dryphasetime
            patch_x3 = dryphasetime + midphasetime
            patch_y1 = patch_y2 = patch_y3 = int(computed["CHARGE_BT"])
            phase_bar_height = 5
            ax1.add_patch(Rectangle((patch_x1, patch_y1), dryphasetime,    phase_bar_height,
                edgecolor = dry_phase_color,
                facecolor = dry_phase_color,
                fill=True,
                lw=1))
            ax1.add_patch(Rectangle((patch_x2, patch_y2), midphasetime,    phase_bar_height,
                edgecolor = mid_phase_color,
                facecolor = mid_phase_color,
                fill=True,
                lw=1))
            ax1.add_patch(Rectangle((patch_x3, patch_y3), finishphasetime, phase_bar_height,
                edgecolor = fin_phase_color,
                facecolor = fin_phase_color,
                fill=True,
                lw=1))

            # phase bar annotation
            dry_time = "%s:%s"%(int(dryphasetime//60), int(dryphasetime%60))
            dry_ratio = "%s%%"%(np.round(dryphasetime/totaltime*100, 1))
            bar_anno_x1 = dryphasetime / 2
            bar_anno_y1 = patch_y1 + 10
            bar_anno_x2 = dryphasetime / 2
            bar_anno_y2 = patch_y1 - 10
            dry_ror = str(computed["dry_phase_ror"]) + mode + "/min"
            ax1.text(bar_anno_x1, bar_anno_y1, dry_time + " " + dry_ratio)
            ax1.text(bar_anno_x2, bar_anno_y2, dry_ror)

            mid_time = "%s:%s"%(int(midphasetime//60), int(midphasetime%60))
            mid_ratio = "%s%%"%(np.round(midphasetime/totaltime*100, 1))
            bar_anno_x1 = dryphasetime + midphasetime / 2
            bar_anno_y1 = patch_y1 + 10
            bar_anno_x2 = dryphasetime + midphasetime / 2
            bar_anno_y2 = patch_y1 - 10
            mid_ror = str(computed["mid_phase_ror"]) + mode + "/min"
            ax1.text(bar_anno_x1, bar_anno_y1, mid_time + " " + mid_ratio)
            ax1.text(bar_anno_x2, bar_anno_y2, mid_ror)

            fin_time = "%s:%s"%(int(finishphasetime//60), int(finishphasetime%60))
            fin_ratio = "%s%%"%(np.round(finishphasetime/totaltime*100, 1))
            bar_anno_x1 = dryphasetime + midphasetime + finishphasetime / 2
            bar_anno_y1 = patch_y1 + 10
            bar_anno_x2 = dryphasetime + midphasetime + finishphasetime / 2
            bar_anno_y2 = patch_y1 - 10
            fin_ror = str(computed["finish_phase_ror"]) + mode + "/min"
            ax1.text(bar_anno_x1, bar_anno_y1, fin_time + " " + fin_ratio)
            ax1.text(bar_anno_x2, bar_anno_y2, fin_ror)
        except KeyError:
            pass

        self.ids.fig.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load_dialog(self):
        content = LoadDialog(load=self.do_load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def do_load(self, path, filename):
        try:
            logfile = os.path.join(path, filename[0])
            with open(logfile, mode="r", encoding="utf-8") as stream:
                log_raw_data_to_json = stream.read().replace("'", "\"")
            log_raw_data_to_json = log_raw_data_to_json.replace("False", "false")
            log_raw_data_to_json = log_raw_data_to_json.replace("True", "true")
            log_json_content = json.loads(log_raw_data_to_json)
            #print(json.dumps(log_json_content, indent=4))

            artisan_os = log_json_content["artisan_os"]
            mode = log_json_content["mode"]
            beans = log_json_content["beans"].encode().decode("unicode_escape")
            weight = log_json_content["weight"]
            roastisodate = log_json_content["roastisodate"]
            timex = log_json_content["timex"]
            temp1 = log_json_content["temp1"] # (ET, color: red)
            temp2 = log_json_content["temp2"] # bean temperture (BT, color: black)
            extratimex = log_json_content["extratimex"] # ROR
            extratemp1 = log_json_content["extratemp1"] # ROR (color: blue)
            phases = log_json_content["phases"]
            zmin = log_json_content["zmin"]
            zmax = log_json_content["zmax"]
            xmin = log_json_content["xmin"]
            xmax = log_json_content["xmax"]
            ymin = log_json_content["ymin"]
            ymax = log_json_content["ymax"]
            computed = log_json_content["computed"]
            anno = log_json_content["anno_positions"]
            roastingnotes = log_json_content["roastingnotes"].encode().decode("unicode_escape")
            #self.ids.scroll_notes.add_widget(
            #        TextInput(text = beans + "\n" + roastingnotes,
            #            width = self.width,
            #            height = 400,
            #            multiline = False, readonly = True))

            global nof
            global notes_popup
            global notes_button
            nof += 1
            print("Load: nof=%s"%(nof))
            notes_popup.append(Popup(title = "Notes",
                    content = Label(text = beans + "\n" + roastingnotes,
                        size_hint_y = 1,
                        halign = "left",
                        valign = "top",
                        text_size = (self.parent.width * 0.7, None),
                        height = self.parent.height * 0.85),
                    size_hint = (0.8, 0.8),
                    auto_dismiss = True))
            notes_button.append(Button(text = str(nof),
                width = self.ids.btn_load.width,
                height = self.ids.btn_load.width,
                size_hint=(None, None)))
            notes_button[nof-1].bind(on_press = notes_popup[nof-1].open)
            self.ids.scroll_notes.add_widget(notes_button[nof-1])

            self.dismiss_popup()
            self.draw2(mode, beans, weight, roastisodate, timex, temp1, temp2, extratimex[0], extratemp1[0], phases, zmin, zmax, xmin, xmax, ymin, ymax, computed, anno)
        except IndexError as e:
            print("E: Index out of range")
        except IOError as e:
            if e.errno == errno.EACCES:
                print("E: Permission denied")
            elif e.errno == errno.ENOENT:
                print("E: File not found")
            else:
                print(e)
        except UnicodeDecodeError:
            print("E: Unsupported encoding")
        except json.decoder.JSONDecodeError:
            print("E: JSON decode failed")
        except KeyError as e:
            print(e)
            if e == 'artisan_os':
                print("E: Invaild log file")
            else:
                print("E: Non-fully supported log")
        finally:
            self.dismiss_popup()

class ViewerApp(App):
    def build(self):
        return ViewerWidget()


if __name__ == "__main__":
    Factory.register("LoadDialog", cls=LoadDialog)
    ViewerApp().run()
