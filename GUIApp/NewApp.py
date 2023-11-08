'''
VasculAR software
Author: Nguyen Le Quoc Bao
Version: 0.2
Competition: Visef & Isef
'''

import customtkinter
import tkinter
from tkinter import filedialog, Canvas
from CTkRangeSlider import *
from draw import draw_canvas
from PIL import Image, ImageTk
import SimpleITK as sitk
from readdcm import ReadDCM
import cv2
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
from cloud_database import LoginPage
import pyrebase
import os

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

firebaseConfig = {
    'apiKey': "AIzaSyCoG09bln3Qrmws87pxnNak-dLC58wCeWE",
    'authDomain': "vascular-68223.firebaseapp.com",
    'databaseURL': "https://vascular-68223-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "vascular-68223",
    'storageBucket': "vascular-68223.appspot.com",
    'messagingSenderId': "1068291063816",
    'appId': "1:1068291063816:web:a1c19e8d2bd465cf7c91bd",
    'measurementId': "G-27VPL4BB1D"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

class AboutWindow(customtkinter.CTkToplevel):
    def __init__(self, parent, title):
        super().__init__()
        self.title(title)
        self.transient(parent)
        self.width = int(self.winfo_screenwidth()/3.5)
        self.height = int(self.winfo_screenheight()/3)
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.iconbitmap('imgs/logo.ico')
        self.protocol("WM_DELETE_WINDOW", self.close_toplevel)
        self.font = customtkinter.ThemeManager.theme["CTkFont"]["family"]
        
        self.frame = customtkinter.CTkFrame(master=self)
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)
        
    def close_toplevel(self):
        self.destroy()
    
class MenuBar:
    def __init__(self, master):
        self.master = master
        self.current_menu = None
        
        self.data = {
            'File': {
                'main_menu': {
                    'instance_name': 'file_btn',
                    'label_name': 'File'
                },
                'sub_menu': {
                    'add_nifti_file_btn': 'Add Nifti file',
                    'add_dcm_series_btn': 'Add DCM series',
                    'save_case_btn': 'Save case',
                    'export_analysis_btn': 'Export analysis',
                }
            },
            'Setting': {
                'main_menu':{
                    'instance_name': 'setting_btn',
                    'label_name': 'Setting'
                }, 
                'sub_menu': {
                    'theme_setting_btn': 'Theme color',
                    'language_setting_btn': 'Language',
                },
                'sub_menu_2': {
                    'theme_setting_btn': {
                        'dark_theme_btn': 'Dark theme',
                        'light_theme_btn': 'Light theme',
                        },
                    'language_setting_btn': {
                        'eng_btn': 'English',
                        'vn_btn': 'Vietnamese',
                    }  
                }         
            },
            'Help': {
                'main_menu': {
                    'instance_name': 'help_btn',
                    'label_name': 'Help'
                },
                'sub_menu': {
                    'basic_functions_btn': 'Basic functions',
                    'defect_dectection_btn': 'Defect detection',
                    'reconstruction_btn': '3D reconstruction',
                    'connection_btn': 'VR & AR connection'
                }
            },
            'About': {
                'main_menu': {
                    'instance_name': 'about_btn',
                    'label_name': 'About', 
                }
            },
            'Account': {
                'main_menu': {
                    'instance_name': 'account_btn',
                    'label_name': 'Account',  
                }
            }
        }
        
        self.menu_item = {'main_menu':{}, 'sub_menu': {}, 'sub_menu_2':{}}
        
        self.create_widget()
        self.layout_widget()
        
    def sub_dropdown_frame(self, widget, row):
        x = self.dropdown.winfo_x() + widget.cget('width')
        y = self.dropdown.winfo_y() + (widget.cget('height') + 5) * row
        instance = widget.cget("text")
        self.menu_item['sub_menu_2'][instance] = customtkinter.CTkFrame(master=self.master)
        self.menu_item['sub_menu_2'][instance].place(x=x,y=y)
        self.menu_item['sub_menu_2'][instance].bind('<Leave>', lambda event : self.menu_item['sub_menu_2'][instance].place_forget())


        print(instance)
        if instance == 'Language':
            self.eng_btn = customtkinter.CTkButton(
                master=self.menu_item['sub_menu_2'][instance],
                text=self.data['Setting']['sub_menu_2']['language_setting_btn']['eng_btn'],
                fg_color='transparent', 
                hover_color=self.master.second_color,
            )
            
            self.eng_btn.pack(padx=5, pady=5)
            self.eng_btn.configure(anchor="w")
            
            self.vn_btn = customtkinter.CTkButton(
                master=self.menu_item['sub_menu_2'][instance],
                text=self.data['Setting']['sub_menu_2']['language_setting_btn']['vn_btn'],
                fg_color='transparent', 
                hover_color=self.master.second_color,
            )
            
            self.vn_btn.pack(padx=5, pady=5)
            self.vn_btn.configure(anchor="w")
            
        if instance == 'Theme color':
            self.eng_btn = customtkinter.CTkButton(
                master=self.menu_item['sub_menu_2'][instance],
                text=self.data['Setting']['sub_menu_2']['theme_setting_btn']['dark_theme_btn'],
                fg_color='transparent', 
                hover_color=self.master.second_color,
            )
            
            self.eng_btn.pack(padx=5, pady=5)
            self.eng_btn.configure(anchor="w")
            
            self.vn_btn = customtkinter.CTkButton(
                master=self.menu_item['sub_menu_2'][instance],
                text=self.data['Setting']['sub_menu_2']['theme_setting_btn']['light_theme_btn'],
                fg_color='transparent', 
                hover_color=self.master.second_color,
            )
            
            self.vn_btn.pack(padx=5, pady=5)
            self.vn_btn.configure(anchor="w")
            
    def choose_file(self):
        self.master.path = filedialog.askopenfilename()
        
        if self.master.path.endswith('.nii.gz') or self.master.path.endswith('.nii'):
            self.master.img_raw = sitk.ReadImage(self.master.path, sitk.sitkFloat32)
            self.master.img = sitk.GetArrayFromImage(self.master.img_raw)
            print("read niftifile")
        
        elif self.master.path.endswith('.dcm'):
            parent_dir = os.path.dirname(self.master.path)
            instance = ReadDCM(parent_dir)
            self.master.img_raw, self.master.img, self.master.dict_info, self.master.pixel_spacing = instance.read_file_dcm()
            print(self.master.dict_info)
            
        self.hide_all_menu()
        self.master.event_generate("<<UpdateApp>>")
        
    def dropdown_options(self, instance, master):            
        for row, (instance_name, label_name) in enumerate(self.data[instance]['sub_menu'].items()):
            if instance_name == 'add_nifti_file_btn':
                self.menu_item['sub_menu'][instance_name] = customtkinter.CTkButton(
                    master=master, 
                    text=label_name,
                    fg_color='transparent', 
                    hover_color=self.master.second_color,
                    command = lambda: self.choose_file(),
                )
            else:
                self.menu_item['sub_menu'][instance_name] = customtkinter.CTkButton(
                    master=master, 
                    text=label_name,
                    fg_color='transparent', 
                    hover_color=self.master.second_color,
                )
            self.menu_item['sub_menu'][instance_name].pack(padx=5, pady=5)
            self.menu_item['sub_menu'][instance_name].configure(anchor="w")
            

    def dropdown_frame(self, widget_option, col):
        self.hide_all_menu()
        if widget_option.cget("text") != 'About' and widget_option.cget("text") != 'Account':
            self.dropdown = customtkinter.CTkFrame(master=self.master)
            x = widget_option.winfo_x() - 10*col
            self.dropdown.place(
                x=x,
                y=30
            )
            self.current_menu = self.dropdown
            if widget_option.cget("text") == 'File':
                self.dropdown_options(
                    instance=widget_option.cget("text"), 
                    master=self.dropdown
                )
                
            elif widget_option.cget("text") == 'Setting':
                self.dropdown_options(
                    instance=widget_option.cget("text"),
                    master=self.dropdown
                )
                self.menu_item['sub_menu']['theme_setting_btn'].bind('<Button-1>', lambda event :self.sub_dropdown_frame(widget=self.menu_item['sub_menu']['theme_setting_btn'], row=0))
                self.menu_item['sub_menu']['language_setting_btn'].bind('<Button-1>', lambda event :self.sub_dropdown_frame(widget=self.menu_item['sub_menu']['language_setting_btn'], row=1))

            elif widget_option.cget("text") == 'Help':
                self.dropdown_options(
                    instance=widget_option.cget("text"),
                    master=self.dropdown
                )

        
        elif widget_option.cget("text") == 'About':
            self.about_window = AboutWindow(
                parent=self.master,
                title='About VasculAR Software',
            )
            
        elif widget_option.cget("text") == 'Account':
            self.login_page = LoginPage(
                parent=self.master,
                title='VasculAR account login',
                auth=auth
            ) 
        
    def hide_all_menu(self):         
        if self.current_menu:
            self.current_menu.place_forget()
            self.current_menu = None

    
    def create_widget(self):
        self.current_menu = None
        self.menu_frame = customtkinter.CTkFrame(master=self.master, fg_color='transparent')
        self.menu_frame.grid(row=0, column=0, columnspan=15, sticky='w')
        self.menu_frame.rowconfigure((0, 1, 2), weight=1, uniform='a')
        
        col=0
        for menu_name, menu_data in self.data.items():
            instance_name = menu_data['main_menu']['instance_name'] 
            self.menu_item['main_menu'][instance_name] = customtkinter.CTkButton(
                master=self.menu_frame,
                text=menu_data['main_menu']['label_name'],
                fg_color='transparent',
                width=10,
                command=lambda instance_name=instance_name, col=col: self.dropdown_frame(widget_option=self.menu_item['main_menu'][instance_name], col=col)
            )
            col += 1
        
        self.master.bind("<Double-Button-1>", lambda event: self.hide_all_menu())
        
        
    def layout_widget(self):
        col=0
        for menu_name, menu_data in self.data.items():
            instance_name = menu_data['main_menu']['instance_name']
            self.menu_item['main_menu'][instance_name].grid(row=0, column=col, padx=(5, 0), sticky='w')
            col+=1
    
class ROI:
    def __init__(self, canvas_view, x1, y1, x2, y2):
        self.canvas_view = canvas_view
        self.main_app = self.canvas_view.master
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.rec_width = self.x2 - self.x1
        self.rec_height = self.y2 - self.y1
        self.circle_width = 10
        self.circle_height = 10
        
        self.rect = self.canvas_view.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, outline='blue', width=5)
        self.nw_circle = self.canvas_view.canvas.create_oval(self.x1-self.circle_width, self.y1-self.circle_height, self.x1+self.circle_width, self.y1+self.circle_height, fill = "blue")
        self.ne_circle = self.canvas_view.canvas.create_oval(self.x1-self.circle_width+self.rec_width, self.y1-self.circle_height, self.x1+self.circle_width+self.rec_width, self.y1+self.circle_height, fill = "blue")
        self.sw_circle = self.canvas_view.canvas.create_oval(self.x1-self.circle_width, self.y1-self.circle_height+self.rec_height, self.x1+self.circle_width, self.y1+self.circle_height+self.rec_height, fill="blue")
        self.se_circle = self.canvas_view.canvas.create_oval(self.x1-self.circle_width+self.rec_width, self.y1-self.circle_height+self.rec_height, self.x1+self.circle_width+self.rec_width, self.y1+self.circle_height+self.rec_height, fill="blue")

        
        if self.canvas_view.master.tools.check_ROI.get() == "on":
            self.move_ne_corner()
            self.move_nw_corner()
            self.move_sw_corner()
            self.move_se_corner()
            
        
    def update(self):
        self.rec_width = self.x2 - self.x1
        self.rec_height = self.y2 - self.y1
        self.canvas_view.canvas.coords(self.nw_circle, self.x1-self.circle_width, self.y1-self.circle_height, self.x1+self.circle_width, self.y1+self.circle_height)
        self.canvas_view.canvas.coords(self.ne_circle, self.x1-self.circle_width+self.rec_width, self.y1-self.circle_height, self.x1+self.circle_width+self.rec_width, self.y1+self.circle_height)
        self.canvas_view.canvas.coords(self.sw_circle, self.x1-self.circle_width, self.y1-self.circle_height+self.rec_height, self.x1+self.circle_width, self.y1+self.circle_height+self.rec_height)
        self.canvas_view.canvas.coords(self.se_circle, self.x1-self.circle_width+self.rec_width, self.y1-self.circle_height+self.rec_height, self.x1+self.circle_width+self.rec_width, self.y1+self.circle_height+self.rec_height)
    
    def move_ne_corner(self):
        def move(event):
            self.canvas_view.canvas.moveto(self.ne_circle, event.x-10, event.y-10)
            self.main_app.corners_data['ne']['x'] = event.x
            self.main_app.corners_data['ne']['y'] = event.y
            
            # update_rec
            self.canvas_view.canvas.coords(self.rect, self.x1, event.y, event.x, self.y2)
            self.main_app.corners_data['rec']['y1'] = event.y
            self.main_app.corners_data['rec']['x2'] = event.x
            
            self.y1 = event.y
            self.x2 = event.x
            
            self.update()
            
        self.canvas_view.canvas.tag_bind(self.ne_circle, '<Button1-Motion>', move)

        
    def move_nw_corner(self):
        def move(event):
            self.canvas_view.canvas.moveto(self.nw_circle, event.x-10, event.y-10)
            self.main_app.corners_data['nw']['x'] = event.x
            self.main_app.corners_data['nw']['y'] = event.y
            
            self.canvas_view.canvas.coords(self.rect, event.x, event.y, self.x2, self.y2)
            self.main_app.corners_data['rec']['x1'] = event.x
            self.main_app.corners_data['rec']['y1'] = event.y
            
            self.x1 = event.x
            self.y1 = event.y
            
            self.update()
            
        
        self.canvas_view.canvas.tag_bind(self.nw_circle, '<Button1-Motion>', move)
        
    def move_sw_corner(self):
        def move(event):
            self.canvas_view.canvas.moveto(self.sw_circle, event.x-10, event.y-10)
            self.main_app.corners_data['sw']['x'] = event.x
            self.main_app.corners_data['sw']['y'] = event.y
            
            self.canvas_view.canvas.coords(self.rect, event.x, self.y1, self.x2, event.y)
            self.main_app.corners_data['rec']['x1'] = event.x
            self.main_app.corners_data['rec']['y2'] = event.y
            
            self.x1 = event.x
            self.y2 = event.y
            
            self.update()
        
        self.canvas_view.canvas.tag_bind(self.sw_circle, '<Button1-Motion>', move)
        
    def move_se_corner(self):
        def move(event):
            self.canvas_view.canvas.moveto(self.se_circle, event.x-10, event.y-10)
            self.main_app.corners_data['se']['x'] = event.x
            self.main_app.corners_data['se']['y'] = event.y
            
            self.canvas_view.canvas.coords(self.rect, self.x1, self.y1,  event.x, event.y)
            self.main_app.corners_data['rec']['x2'] = event.x
            self.main_app.corners_data['rec']['y2'] = event.y
            
            self.x2 = event.x
            self.y2 = event.y
            
            self.update()
        
        self.canvas_view.canvas.tag_bind(self.se_circle, '<Button1-Motion>', move)


class CanvasAxial:
    def __init__(self, master):
        self.master = master
        self.create_frame()
        self.create_tool_widgets()
        self.create_canvas()     
        
    def create_tool_widgets(self):
        def rotation():
            def rotation_control():
                current_val = int(self.rotation_label.cget('text'))
                if current_val == 360:
                    current_val = 0
                self.rotation_label.configure(text=current_val+90)
            
            self.rotation_label = customtkinter.CTkLabel(master=self.frame, text="0") 
            self.rotation_btn = customtkinter.CTkButton(master=self.frame_tools, text='R', width=30, command=rotation_control)
            self.rotation_btn.grid(column=0, row=0, sticky='w') 

        def flip_horizontal():
            def flip_control():
                cur_val = self.flip_horizontal_label.cget("text")
                if cur_val == "":  
                    self.flip_horizontal_label.configure(text="horizontal")
                else:
                    self.flip_horizontal_label.configure(text="")
                
            self.flip_horizontal_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_horizontal_btn = customtkinter.CTkButton(master=self.frame_tools, text='H', width=30, command=flip_control)
            self.flip_horizontal_btn.grid(column=1, row=0, sticky='w')  
            
        def flip_vertical():
            def flip_control():
                cur_val = self.flip_vertical_label.cget("text")
                if cur_val == "":
                    self.flip_vertical_label.configure(text="vertical")
                else:
                    self.flip_vertical_label.configure(text="")
                    
            self.flip_vertical_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_vertical_btn = customtkinter.CTkButton(master=self.frame_tools, text='V', width=30, command=flip_control)
            self.flip_vertical_btn.grid(column=2, row=0, sticky='w')  

        self.frame_tools = customtkinter.CTkFrame(master=self.master, fg_color='transparent')
        self.frame_tools.grid(column=4, row=0, columnspan=1, rowspan=1, pady=(35, 0), sticky='news')
        self.frame_tools.columnconfigure((0,1,2), weight=1)
        rotation()
        flip_horizontal()
        flip_vertical()
        
    def create_frame(self):
        self.frame = customtkinter.CTkFrame(master=self.master, fg_color=self.master.second_color)
        self.frame.grid(row=1, column=0, rowspan=9, columnspan=6, padx=5, sticky='news')
        
    def create_canvas(self):    
        def create_crosshair():           
            def move_crosshair(event):
                x, y = event.x, event.y
                self.canvas.coords(self.horizontal_line, 0, y, self.canvas.winfo_width(), y)
                self.canvas.coords(self.vertical_line, x, 0, x, self.canvas.winfo_height())

            def on_mouse_press(event):
                if self.master.tools.check_ROI.get() == "off":
                    self.canvas.bind("<Motion>", move_crosshair)

            def on_mouse_release(event):
                if self.master.tools.check_ROI.get() == "off":
                    self.canvas.unbind("<Motion>")
            
            self.horizontal_line = self.canvas.create_line(0, self.canvas.winfo_height() // 2, self.canvas.winfo_width(), self.canvas.winfo_height() // 2, fill="red")
            self.vertical_line = self.canvas.create_line(self.canvas.winfo_width() // 2, 0, self.canvas.winfo_width() // 2, self.canvas.winfo_height(), fill="red")
            self.canvas.bind("<ButtonPress-1>", on_mouse_press)
            self.canvas.bind("<ButtonRelease-1>", on_mouse_release)          
            
        def image_display(index_slice):
            # get size
            height = int(self.label_zoom.cget("text"))
            # slice index
            image = self.master.img[int(index_slice),:, :]
            # color map
            plt.imsave("temp.jpg", image, cmap='gray')
            # resize
            image_display = Image.open("temp.jpg").resize((height, height))
            
            # rotate
            rotation_angle = int(self.rotation_label.cget("text"))
            image_display = image_display.rotate(rotation_angle)
            
            # flip
            horizontal = self.flip_horizontal_label.cget("text")
            vertical = self.flip_vertical_label.cget("text")
            if horizontal == "horizontal":
                image_display = image_display.transpose(Image.FLIP_LEFT_RIGHT)
            if vertical == "vertical":
                image_display = image_display.transpose(Image.FLIP_TOP_BOTTOM)

            # diplay image
            my_image = ImageTk.PhotoImage(image_display)
            x_cord, y_cord = image_position()
            self.canvas_item = self.canvas.create_image(x_cord, y_cord, image=my_image, anchor="center")
            self.canvas.image = my_image
            
            # create crosshair
            create_crosshair()
            
            # display info
            display_info()
            
            # ROI
            self.region_of_interest = ROI(self, 
                self.master.corners_data['rec']['x1'], 
                self.master.corners_data['rec']['y1'],
                self.master.corners_data['rec']['x2'], 
                self.master.corners_data['rec']['y2']
            )
            
            self.canvas.configure(bg='black')
            
            
        def image_position():
            try:
                image_position = self.canvas.coords(self.canvas_item)
                return image_position[0], image_position[1]
            except:
                return 400, 400
            
        def movement_binding():
            self.canvas.bind('<Left>', lambda event: self.canvas.move(self.canvas_item, -10, 0))
            self.canvas.bind('<Right>', lambda event: self.canvas.move(self.canvas_item, 10, 0))
            self.canvas.bind('<Up>', lambda event: self.canvas.move(self.canvas_item, 0, -10))
            self.canvas.bind('<Down>', lambda event: self.canvas.move(self.canvas_item, 0, 10))   
            
        def display_info():
            text_item = self.canvas.create_text(10, 20, text='AXIAL VIEW', anchor="w", fill=self.master.text_canvas_color)
            y = 40
            for k, v in self.master.dict_info.items():
                text_item = self.canvas.create_text(10, y, text=f'{k} : {v}', anchor="w", fill=self.master.text_canvas_color)
                y += 20
        
        def zoom(event):
            current_value = self.label_zoom.cget("text")
            new_value = int(current_value) + (event.delta/120)*6
            self.label_zoom.configure(text=new_value)
            image_display(self.slider_volume.get())   
            
        def slider_volume_show(value):
            index_slice = round(value, 0)
            self.text_show_volume.configure(text=int(index_slice))
            self.canvas.focus_set() 
            image_display(index_slice)

        def slider_widget():        
            self.slider_volume = customtkinter.CTkSlider(self.master, from_=0, to=self.master.img.shape[0]-1, command=slider_volume_show)
            self.slider_volume.grid(column=0, row=0, columnspan=2, rowspan=1, padx=(5,0), pady=(25,0), sticky='ew')
            self.text_show_volume = customtkinter.CTkLabel(self.master, text="")
            self.text_show_volume.grid(column=2, row=0, rowspan=1, pady=(25,0), sticky='ew')
            
        self.canvas = Canvas(master=self.frame, bd=0, bg=self.master.first_color)
        self.canvas.pack(fill='both', expand=True)
        
        self.label_zoom = customtkinter.CTkLabel(master=self.frame, text="900")
        self.canvas.bind("<MouseWheel>", zoom)
        
        movement_binding()
        slider_widget()

class CanvasSagittal:
    def __init__(self, master):
        self.master = master
        self.create_frame()
        self.create_canvas()     
        self.create_tool_widgets()
        
    def create_tool_widgets(self):
        def rotation():
            def rotation_control():
                current_val = int(self.rotation_label.cget('text'))
                if current_val == 360:
                    current_val = 0
                self.rotation_label.configure(text=current_val+90)
            
            self.rotation_label = customtkinter.CTkLabel(master=self.frame, text="0") 
            self.rotation_btn = customtkinter.CTkButton(master=self.frame_tools, text='R', width=30, command=rotation_control)
            self.rotation_btn.grid(column=0, row=0, sticky='w') 

        def flip_horizontal():
            def flip_control():
                cur_val = self.flip_horizontal_label.cget("text")
                if cur_val == "":  
                    self.flip_horizontal_label.configure(text="horizontal")
                else:
                    self.flip_horizontal_label.configure(text="")
                
            self.flip_horizontal_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_horizontal_btn = customtkinter.CTkButton(master=self.frame_tools, text='H', width=30, command=flip_control)
            self.flip_horizontal_btn.grid(column=1, row=0, sticky='w')  
            
        def flip_vertical():
            def flip_control():
                cur_val = self.flip_vertical_label.cget("text")
                if cur_val == "":
                    self.flip_vertical_label.configure(text="vertical")
                else:
                    self.flip_vertical_label.configure(text="")
                    
            self.flip_vertical_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_vertical_btn = customtkinter.CTkButton(master=self.frame_tools, text='V', width=30, command=flip_control)
            self.flip_vertical_btn.grid(column=2, row=0, sticky='w')  

        self.frame_tools = customtkinter.CTkFrame(master=self.master, fg_color='transparent')
        self.frame_tools.grid(column=10, row=0, columnspan=1, rowspan=1, pady=(35, 0), sticky='news')
        self.frame_tools.columnconfigure((0,1,2), weight=1)
        rotation()
        flip_horizontal()
        flip_vertical() 

    def create_frame(self):
        self.frame = customtkinter.CTkFrame(master=self.master, fg_color='transparent')
        self.frame.grid(row=1, column=6, rowspan=9, columnspan=6, padx=5, sticky='news')
        
    def create_canvas(self):    
        def create_crosshair():
            self.horizontal_line = self.canvas.create_line(0, self.canvas.winfo_height() // 2, self.canvas.winfo_width(), self.canvas.winfo_height() // 2, fill="red")
            self.vertical_line = self.canvas.create_line(self.canvas.winfo_width() // 2, 0, self.canvas.winfo_width() // 2, self.canvas.winfo_height(), fill="red")
            
            def move_crosshair(event):
                x, y = event.x, event.y
                self.canvas.coords(self.horizontal_line, 0, y, self.canvas.winfo_width(), y)
                self.canvas.coords(self.vertical_line, x, 0, x, self.canvas.winfo_height())

            def on_mouse_press(event):
                self.canvas.bind("<Motion>", move_crosshair)

            def on_mouse_release(event):
                self.canvas.unbind("<Motion>")

            self.canvas.bind("<ButtonPress-1>", on_mouse_press)
            self.canvas.bind("<ButtonRelease-1>", on_mouse_release)                
            
        def image_display(index_slice):
            # get size
            height = int(self.label_zoom.cget("text"))
            # slice index
            image = self.master.img[:,int(index_slice),:]
            # color map
            plt.imsave("temp.jpg", image, cmap='gray')
            # resize
            image_display = Image.open("temp.jpg").resize((height, height))
            
            # rotate
            rotation_angle = int(self.rotation_label.cget("text"))
            image_display = image_display.rotate(rotation_angle)
            
            # flip
            horizontal = self.flip_horizontal_label.cget("text")
            vertical = self.flip_vertical_label.cget("text")
            if horizontal == "horizontal":
                image_display = image_display.transpose(Image.FLIP_LEFT_RIGHT)
            if vertical == "vertical":
                image_display = image_display.transpose(Image.FLIP_TOP_BOTTOM)

            # diplay image
            my_image = ImageTk.PhotoImage(image_display)
            x_cord, y_cord = image_position()
            self.canvas_item = self.canvas.create_image(x_cord, y_cord, image=my_image, anchor="center")
            self.canvas.image = my_image
            
            # create crosshair
            create_crosshair()
            
            # display info
            display_info()
            self.canvas.configure(bg='black')
            
            
        def image_position():
            try:
                image_position = self.canvas.coords(self.canvas_item)
                return image_position[0], image_position[1]
            except:
                return 400, 400
            
        def movement_binding():
            self.canvas.bind('<Left>', lambda event: self.canvas.move(self.canvas_item, -10, 0))
            self.canvas.bind('<Right>', lambda event: self.canvas.move(self.canvas_item, 10, 0))
            self.canvas.bind('<Up>', lambda event: self.canvas.move(self.canvas_item, 0, -10))
            self.canvas.bind('<Down>', lambda event: self.canvas.move(self.canvas_item, 0, 10))   
            
        def display_info():
            text_item = self.canvas.create_text(10, 20, text='SAGITTAL VIEW', anchor="w", fill=self.master.text_canvas_color)
            y = 40
            for k, v in self.master.dict_info.items():
                text_item = self.canvas.create_text(10, y, text=f'{k} : {v}', anchor="w", fill=self.master.text_canvas_color)
                y += 20
        
        def zoom(event):
            current_value = self.label_zoom.cget("text")
            new_value = int(current_value) + (event.delta/120)*6
            self.label_zoom.configure(text=new_value)
            image_display(self.slider_volume.get())   
            
        def slider_volume_show(value):
            index_slice = round(value, 0)
            self.text_show_volume.configure(text=int(index_slice))
            self.canvas.focus_set() 
            image_display(index_slice)

        def slider_widget():        
            self.slider_volume = customtkinter.CTkSlider(self.master, from_=0, to=self.master.img.shape[1]-1, command=slider_volume_show)
            self.slider_volume.grid(column=6, row=0, columnspan=2, rowspan=1, padx=(5,0), pady=(25,0), sticky='ew')
            self.text_show_volume = customtkinter.CTkLabel(self.master, text="")
            self.text_show_volume.grid(column=8, row=0, rowspan=1, pady=(25,0), sticky='ew')
            
        self.canvas = Canvas(master=self.frame, bd=0, bg=self.master.first_color)
        self.canvas.pack(fill='both', expand=True)
        
        self.label_zoom = customtkinter.CTkLabel(master=self.frame, text="900")
        self.canvas.bind("<MouseWheel>", zoom)
        
        movement_binding()
        slider_widget()
        
class CanvasCoronal:
    def __init__(self, master):
        self.master = master
        self.create_frame()
        self.create_tool_widgets()
        self.create_canvas()     

    def create_tool_widgets(self):
        def rotation():
            def rotation_control():
                current_val = int(self.rotation_label.cget('text'))
                if current_val == 360:
                    current_val = 0
                self.rotation_label.configure(text=current_val+90)
            
            self.rotation_label = customtkinter.CTkLabel(master=self.frame, text="0") 
            self.rotation_btn = customtkinter.CTkButton(master=self.frame_tools, text='R', width=30, command=rotation_control)
            self.rotation_btn.grid(column=0, row=0, sticky='w') 

        def flip_horizontal():
            def flip_control():
                cur_val = self.flip_horizontal_label.cget("text")
                if cur_val == "":  
                    self.flip_horizontal_label.configure(text="horizontal")
                else:
                    self.flip_horizontal_label.configure(text="")
                
            self.flip_horizontal_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_horizontal_btn = customtkinter.CTkButton(master=self.frame_tools, text='H', width=30, command=flip_control)
            self.flip_horizontal_btn.grid(column=1, row=0, sticky='w')  
            
        def flip_vertical():
            def flip_control():
                cur_val = self.flip_vertical_label.cget("text")
                if cur_val == "":
                    self.flip_vertical_label.configure(text="vertical")
                else:
                    self.flip_vertical_label.configure(text="")
                    
            self.flip_vertical_label = customtkinter.CTkLabel(master=self.frame, text="") 
            self.flip_vertical_btn = customtkinter.CTkButton(master=self.frame_tools, text='V', width=30, command=flip_control)
            self.flip_vertical_btn.grid(column=2, row=0, sticky='w')  

        self.frame_tools = customtkinter.CTkFrame(master=self.master, fg_color='transparent')
        self.frame_tools.grid(column=16, row=0, columnspan=1, rowspan=1, pady=(35, 0), sticky='news')
        self.frame_tools.columnconfigure((0,1,2), weight=1)
        rotation()
        flip_horizontal()
        flip_vertical() 
        
    def create_frame(self):
        self.frame = customtkinter.CTkFrame(master=self.master, fg_color=self.master.second_color)
        self.frame.grid(row=1, column=12, rowspan=9, columnspan=6, padx=5, sticky='news')
        
    def create_canvas(self):    
        def create_crosshair():
            self.horizontal_line = self.canvas.create_line(0, self.canvas.winfo_height() // 2, self.canvas.winfo_width(), self.canvas.winfo_height() // 2, fill="red")
            self.vertical_line = self.canvas.create_line(self.canvas.winfo_width() // 2, 0, self.canvas.winfo_width() // 2, self.canvas.winfo_height(), fill="red")
            
            def move_crosshair(event):
                x, y = event.x, event.y
                self.canvas.coords(self.horizontal_line, 0, y, self.canvas.winfo_width(), y)
                self.canvas.coords(self.vertical_line, x, 0, x, self.canvas.winfo_height())

            def on_mouse_press(event):
                self.canvas.bind("<Motion>", move_crosshair)

            def on_mouse_release(event):
                self.canvas.unbind("<Motion>")

            self.canvas.bind("<ButtonPress-1>", on_mouse_press)
            self.canvas.bind("<ButtonRelease-1>", on_mouse_release)                
            
        def image_display(index_slice):
            # get size
            height = int(self.label_zoom.cget("text"))
            # slice index
            image = self.master.img[:,:,int(index_slice)]
            # color map
            plt.imsave("temp.jpg", image, cmap='gray')
            # resize
            image_display = Image.open("temp.jpg").resize((height, height))
            
            # rotate
            rotation_angle = int(self.rotation_label.cget("text"))
            image_display = image_display.rotate(rotation_angle)
            
            # flip
            horizontal = self.flip_horizontal_label.cget("text")
            vertical = self.flip_vertical_label.cget("text")
            if horizontal == "horizontal":
                image_display = image_display.transpose(Image.FLIP_LEFT_RIGHT)
            if vertical == "vertical":
                image_display = image_display.transpose(Image.FLIP_TOP_BOTTOM)

            # diplay image
            my_image = ImageTk.PhotoImage(image_display)
            x_cord, y_cord = image_position()
            self.canvas_item = self.canvas.create_image(x_cord, y_cord, image=my_image, anchor="center")
            self.canvas.image = my_image
            
            # create crosshair
            create_crosshair()
            
            # display info
            display_info()
            self.canvas.configure(bg='black')
            
            
        def image_position():
            try:
                image_position = self.canvas.coords(self.canvas_item)
                return image_position[0], image_position[1]
            except:
                return 400, 400
            
        def movement_binding():
            self.canvas.bind('<Left>', lambda event: self.canvas.move(self.canvas_item, -10, 0))
            self.canvas.bind('<Right>', lambda event: self.canvas.move(self.canvas_item, 10, 0))
            self.canvas.bind('<Up>', lambda event: self.canvas.move(self.canvas_item, 0, -10))
            self.canvas.bind('<Down>', lambda event: self.canvas.move(self.canvas_item, 0, 10))   
            
        def display_info():
            text_item = self.canvas.create_text(10, 20, text='CORONAL VIEW', anchor="w", fill=self.master.text_canvas_color)
            y = 40
            for k, v in self.master.dict_info.items():
                text_item = self.canvas.create_text(10, y, text=f'{k}:{v}', anchor="w", fill=self.master.text_canvas_color)
                y += 20
        
        def zoom(event):
            current_value = self.label_zoom.cget("text")
            new_value = int(current_value) + (event.delta/120)*6
            self.label_zoom.configure(text=new_value)
            image_display(self.slider_volume.get())   
            
        def slider_volume_show(value):
            index_slice = round(value, 0)
            self.text_show_volume.configure(text=int(index_slice))
            self.canvas.focus_set() 
            image_display(index_slice)
            

        def slider_widget():        
            self.slider_volume = customtkinter.CTkSlider(self.master, from_=0, to=self.master.img.shape[2]-1, command=slider_volume_show)
            self.slider_volume.grid(column=12, row=0, columnspan=2, rowspan=1, padx=(5,0), pady=(25,0), sticky='ew')
            self.text_show_volume = customtkinter.CTkLabel(self.master, text="")
            self.text_show_volume.grid(column=14, row=0, rowspan=1, pady=(25,0), sticky='ew')
            
        self.canvas = Canvas(master=self.frame, bd=0, bg=self.master.first_color)
        self.canvas.pack(fill='both', expand=True)
        
        self.label_zoom = customtkinter.CTkLabel(master=self.frame, text="900")
        self.canvas.bind("<MouseWheel>", zoom)
        
        movement_binding()
        slider_widget()
        
    
        
class Tools:
    def __init__(self, master):
        self.master = master
        self.TabView1()
        self.TabView2()
        
    def TabView1(self):
        def DrawingTools():
            self.check_var = customtkinter.StringVar(value="off")
            self.check_ROI = customtkinter.CTkCheckBox(master=self.tab_1, text="Edit ROI", variable=self.check_var, onvalue="on", offvalue="off")
            self.check_ROI.pack()
            
        self.tabview_1 = customtkinter.CTkTabview(master=self.master)
        self.tabview_1.grid(column=0, row=10, columnspan=9, rowspan=5, padx=5, pady=5, sticky="nsew")
        self.tab_1 = self.tabview_1.add("Basic tools")    
        self.tab_2 = self.tabview_1.add("Image processing")
        self.tab_3 = self.tabview_1.add("Defect Detection")
        self.tabview_1.set("Basic tools") 
        DrawingTools()
        
    def TabView2(self):
        self.tabview_2 = customtkinter.CTkTabview(master=self.master)
        self.tabview_2.grid(column=9, row=10, columnspan=9, rowspan=5, padx=5, pady=5, sticky="nsew")
        self.tab_1 = self.tabview_2.add("Segmentation")    
        self.tab_2 = self.tabview_2.add("3D reconstruction")
        self.tab_3 = self.tabview_2.add("VR/AR connection")
        self.tabview_2.set("Segmentation") 
    
class App(customtkinter.CTk):
    def __init__(self, title, logo_path):
        super().__init__()
        self.title(title)
        self.width = int(self.winfo_screenwidth()/1.05)
        self.height = int(self.winfo_screenheight()/1.1)
        self.geometry(f"{self.width}x{self.height}")
        self.minsize(500, 500)
        self.iconbitmap(logo_path)
        
        self.first_color = "#2b2b2b"
        self.second_color = "#3b3b3b"
        self.text_disabled_color = "#dce4e2"
        self.text_canvas_color = "yellow"
        
        
        self.img = None
        self.img_raw = None
        self.dict_info = {
            "Organization": "Benh vien Cho Ray",
            "Patient's name": "Ton That Hung",
            "Modality": "MRI",
            "Patient ID": "0000097031",
            "Body Part Examined": "CHEST_TO_PELVIS",
            "Acquisition Date": "20231019"
        }
        self.pixel_spacing = 0.858
        self.path = ''
        self.corners_data = {
            'rec': {
                'x1': 50,
                'y1': 50,
                'x2': 500,
                'y2': 500,
            },
            'nw': {
                'x': 0,
                'y': 0,
            },
            'ne': {
                'x': 0,
                'y': 0,
            },
            'sw': {
                'x': 0,
                'y': 0,
            },
            'se': {
                'x': 0,
                'y': 0,
            }
        }

        # column and rows
        for i in range(15):
            self.rowconfigure(i, weight=1, uniform='a')
            
        for i in range(18):
            self.columnconfigure(i, weight=1, uniform='a')
            
        # for i in range(15):
        #     for j in range(18):
        #         label = customtkinter.CTkFrame(self, fg_color="transparent")
        #         label.grid(row=i, column=j, sticky='nsew')

        # create menu
        self.menu_bar = MenuBar(self)
        self.tools = Tools(self)
        
        def update_app(event):
            self.axial = CanvasAxial(self)
            self.sagittal = CanvasSagittal(self)
            self.coronal = CanvasCoronal(self)
            
            
        self.bind("<<UpdateApp>>", update_app)
        self.mainloop()

app = App(
    title='VasculAR software',
    logo_path='imgs/logo.ico'
)
