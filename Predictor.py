from tkinter import *
from tkinter import ttk
from PIL import Image, ImageDraw
import numpy as np
from tensorflow import keras

class Paint():

    def __init__(self):
        self.root = Tk()
        self.root.title("Letter Predictor")

        self.pen_button = Button(self.root, text='Pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.eraser_button = Button(self.root, text='Eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1)

        self.clear_button = Button(self.root, text='Clear', command=self.clear_canvas)
        self.clear_button.grid(row=0, column=2)

        self.predict_button = Button(self.root, text='Predict', command=self.predict_letter)
        self.predict_button.grid(row=0, column=3)

        self.c = Canvas(self.root, bg='black', width=588, height=588)
        self.c.grid(row=1, columnspan=5)

        self.image1 = Image.new("RGB", (588, 588), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image1)

        self.model = keras.models.load_model('model.keras')

        map_file = open("mapping.txt", "r")
        lines = map_file.readlines()
        map_file.close()
        self.map_dict = {int(line.split(' ')[0]): int(line.split(' ')[1]) for line in lines}

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.color = 'white'
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def clear_canvas(self):
        self.activate_button(self.clear_button)
        self.c.delete("all")
        self.image1 = Image.new("RGB", (588, 588), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image1)

    def open_window(self, prediction):
        root = Tk()
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        text = "The letter/number is: " + prediction
        ttk.Label(frm, text=text).grid(column=0, row=0)
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
        root.title("Prediction")
        root.mainloop()

    def predict_letter(self):
        self.activate_button(self.predict_button)        
        self.image1 = self.image1.convert("L").resize((28, 28), Image.LANCZOS)

        img_arr = np.asarray(self.image1, dtype="float32")
        img_arr = img_arr.astype("float32") / 255
        img_arr = img_arr.reshape(1, 28, 28)        

        prediction = self.model.predict(img_arr)
        pred_list = prediction[0].tolist()
        pred_num = pred_list.index(max(pred_list))
        char_predicted = chr(self.map_dict[pred_num])
        
        self.clear_canvas()
        self.open_window(char_predicted)


    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        paint_color = 'black' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=42, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
            
            self.draw.line(xy=(self.old_x, self.old_y, event.x, event.y), 
                    fill=paint_color, width = 42) 
            
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()