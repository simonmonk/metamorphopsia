from tkinter import * 
from tkinter.filedialog import asksaveasfile, askopenfile
from datetime import datetime
import json
from PIL import Image
import os

num_lines = 21
dx = 30 # pixels
width = (num_lines-1) * dx # pixels
mid_x = int(num_lines / 2) * dx
dot_r = dx / 10 # pixels
bump_r = 2 * dx
date = datetime.now().strftime("%Y-%m-%d")
title_base = "Metamorphopsia Measurement Tool"

selected_x_line_num = None
selected_y_line_num = None

window = Tk() 
window.title('Metamorphopsia Measurement Tool') 
window.geometry(str(width) + "x" + str(width + 100)) 

# offset and value
h_lines = [ {'offset': 0, 'value': 0} for x in range(num_lines)]
v_lines = [ {'offset': 0, 'value': 0} for x in range(num_lines)]

canvas = Canvas(window, bg="white", height=width, width=width) 
button_frame = Frame(window)

def set_window_title():
    title = title_base + " (" + date + ")"
    window.title(title)

def reset():
    global h_lines, v_lines
    h_lines = [ {'offset': 0, 'value': 0} for x in range(num_lines)]   
    v_lines = [ {'offset': 0, 'value': 0} for x in range(num_lines)]    
    draw_lines()    

def save_as():
    now = datetime.now() # current date and time
    timestamp_str = now.strftime("%Y-%m-%d")
    file = asksaveasfile(initialfile = timestamp_str,
        initialdir='.',
        defaultextension=".met",
        filetypes=[("Metamorphopsia JSON","*.met")])
    data = {'bump_r': bump_r, 'h_lines': h_lines, 'v_lines': v_lines, 'date': date}
    if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    json.dump(data, file)
    file.close()
    

def open_file():
    global h_lines, v_lines, bump_r, date
    file = askopenfile(initialdir='.',
        defaultextension=".met",
        filetypes=[("Metamorphopsia JSON","*.met")])
    if file is None: # return `None` if dialog closed with "cancel".
        return
    data = json.load(file)
    bump_r = data['bump_r']
    h_lines = data['h_lines']
    v_lines = data['v_lines']
    date = data['date']
    draw_lines()
    file.close()    
    set_window_title()

def export_image():
    now = datetime.now() # current date and time
    timestamp_str = now.strftime("%Y-%m-%d")
    file = asksaveasfile(initialfile = timestamp_str,
        initialdir='.',
        defaultextension=".png",
        filetypes=[("PNG","*.png")])
    if file is None: # return `None` if dialog closed with "cancel".
        return
    canvas.postscript(file=file.name + '.eps')
    img = Image.open(file.name + '.eps') 
    img.save(file.name, 'png') 
    os.remove(file.name + '.eps')

def draw_lines():
    canvas.delete('all')
    for line_num in range(num_lines-1):
        draw_h_line(line_num)
        draw_v_line(line_num)
    draw_dot()

def draw_dot():
    mid_x_line = h_lines[10]
    crossing_x = mid_x
    crossing_y = mid_x
    canvas.create_oval(crossing_x-dot_r, crossing_y-dot_r, crossing_x+dot_r, crossing_y+dot_r, fill="red")

def draw_h_line(line_num):
    y = line_num * dx
    line = h_lines[line_num]
    left = (0, y)
    right = (width-1, y)
    distortion_0 = ((mid_x + line['offset'] - bump_r), y)
    distortion = ((mid_x + line['offset']), (y + line['value']))
    distortion_1 = ((mid_x + line['offset'] + bump_r), y)
    color = 'black'
    if selected_x_line_num == line_num:
        color = 'blue'
    canvas.create_line(left, distortion_0, distortion, distortion_1, right, fill=color, smooth="bezier")

def draw_v_line(line_num):
    x = line_num * dx
    line = v_lines[line_num]
    top = (x, 0)
    bottom = (x, width-1)
    distortion_0 = (x, (mid_x + line['offset'] - bump_r))
    distortion = ((x + line['value']), (mid_x + line['offset']))
    distortion_1 = (x, (mid_x + line['offset'] + bump_r))
    color = 'black'
    if selected_y_line_num == line_num:
        color = 'blue'
    canvas.create_line(top, distortion_0, distortion, distortion_1, bottom, fill=color, smooth="bezier")


# def draw_v_line(line_num):
#     canvas.create_line(line_num * dx, 0, line_num * dx, width-1)

def click(event):
    global selected_x_line_num, selected_y_line_num
    x, y = event.x, event.y
    if axis.get() == 'x':
        selected_x_line_num = round(y / dx)
    else:  
        selected_y_line_num = round(x / dx)

def motion(event):
    x, y = event.x, event.y
    if axis.get() == 'x':
        if not selected_x_line_num:
            return
        selected_line = h_lines[selected_x_line_num]
        x_offset_pixels = x - mid_x
        y_offset_pixels = y - (selected_x_line_num * dx)
        selected_line['offset'] = x_offset_pixels
        selected_line['value'] = y_offset_pixels
    else:
        if not selected_y_line_num:
            return
        selected_line = v_lines[selected_y_line_num]
        x_offset_pixels = x - (selected_y_line_num * dx)
        y_offset_pixels = y - mid_x
        selected_line['offset'] = y_offset_pixels
        selected_line['value'] = x_offset_pixels
    draw_lines()

canvas.bind('<B1-Motion>', motion)
canvas.bind('<Button-1>', click)

def changed_bump(w):
    global bump_r
    bump_r = int(w)
    draw_lines()

axis = StringVar(window, 'x')

axis_frame = Frame(button_frame)
x_button = Radiobutton(axis_frame, text="Horizontal Lines", variable=axis, value='x')
x_button.pack(fill='both')
y_button = Radiobutton(axis_frame, text="Vertical Lines", variable=axis, value='y')
y_button.pack(fill='both')

axis_frame.pack(side='left')

width_label = Label(button_frame, text="Bump Width")
width_label.pack(side='left')

bump_width_scale = Scale(button_frame, from_=dx, to=dx*5, command=changed_bump, orient=HORIZONTAL)
bump_width_scale.pack(side='left')

reset_button = Button(button_frame, command = reset, height = 2,  width = 10, text = "Reset")
reset_button.pack(side='left')

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Reset", command=reset)
filemenu.add_command(label="Open...", command=open_file)
filemenu.add_command(label="Save as...", command=save_as)
filemenu.add_command(label="Export Image...", command=export_image)

filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)
window.config(menu=menubar)
draw_lines()
canvas.pack()
button_frame.pack(side='top', fill='x')
window.mainloop() 