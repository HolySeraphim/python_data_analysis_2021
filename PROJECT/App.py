from PIL import Image
import numpy as np
import io
from telebot import types


class App:
    def __init__(self, bot):
        self.photo_info_send = {}  # pathway
        self.last_photo_send = {}  # last photo
        self.latter_to_use = {}  # False or True
        self.bot = bot
        self.funcs = {'nothing': self.__nothing,
                      '↔': self.__rot_hor,
                      '↕': self.__rot_ver,
                      'red': self.__red,
                      'green': self.__green,
                      'blue': self.__blue,
                      'grey': self.__grey,
                      'black and white': self.__BLMethod,
                      'negative': self.__negative,
                      'sepia': self.__sepia,
                      'grey_red': self.__grey_red,
                      'circle': self.__circle}
        self.markup = self.__get_markup()

    def add(self, chat, path):  # add to dict
        self.photo_info_send[chat] = path

    def add_last_send(self, chat, photo):  # add to dict
        self.last_photo_send[chat] = photo

    def use_the_latter(self, chat, mode):  # user`s choice
        if mode:
            self.latter_to_use[chat] = True
        elif chat in self.latter_to_use.keys():
            self.latter_to_use[chat] = False

    def change(self, mode, chat):  # photo changing

        if chat in self.latter_to_use.keys() and self.latter_to_use[chat] and chat in self.last_photo_send.keys():
            data = np.asarray(self.last_photo_send[chat])
            return self.funcs[mode](data)

        if chat in self.photo_info_send.keys():
            file = self.bot.download_file(self.photo_info_send[chat])
            image = Image.open(io.BytesIO(file))
            data = np.asarray(image)
            return self.funcs[mode](data)
        return None

    def __get_markup(self):  # keyboard generation from dict
        markup = types.InlineKeyboardMarkup(row_width=3)
        commands = list(self.funcs.keys())
        i = 0
        buttons = []
        for command in commands:
            buttons.append(types.InlineKeyboardButton(command, callback_data=command))
            i += 1
            if i % 3 == 0:
                markup.add(buttons[0], buttons[1], buttons[2])
                buttons.clear()
        if len(buttons) == 2:
            markup.add(buttons[0], buttons[1])
        if len(buttons) == 1:
            markup.add(buttons[0])
        return(markup)

    def __nothing(self, data):
        return Image.fromarray(data)

    def __grey(self, data):
        grey = np.dot(data, [0.29, 0.58, 0.11])
        return Image.fromarray(grey)

    def __red(self, data):
        c = 0
        color_img = np.zeros_like(data)
        color_img[..., c] = data[..., c]
        return Image.fromarray(color_img)

    def __green(self, data):
        c = 1
        color_img = np.zeros_like(data)
        color_img[..., c] = data[..., c]
        return Image.fromarray(color_img)

    def __blue(self, data):
        c = 2
        color_img = np.zeros_like(data)
        color_img[..., c] = data[..., c]
        return Image.fromarray(color_img)

    def __circle(self, data):
        lx, ly, lz = data.shape

        # Mask
        X, Y = np.ogrid[0:lx, 0:ly]
        mask = (X - lx / 2) ** 2 + (Y - ly / 2) ** 2 > lx * ly / 4  # задаем круг

        img_circle = data.copy()
        img_circle[mask] = 0
        return Image.fromarray(img_circle)

    def __negative(self, data):
        negative_img = np.zeros_like(data) + 255
        negative_img -= data
        return Image.fromarray(negative_img)

    def __rot_hor(self, data):
        rot_img = np.fliplr(data)
        return Image.fromarray(rot_img)

    def __rot_ver(self, data):
        rot_img = np.flipud(data)
        return Image.fromarray(rot_img)

    def __sepia(self, data):
        sepia = np.zeros_like(data)

        temp = np.dot(data, [0.393, 0.769, 0.189])
        temp[temp > 255] = 255
        sepia[..., 0] = temp

        temp = np.dot(data, [0.349, 0.686, 0.168])
        temp[temp > 255] = 255
        sepia[..., 1] = temp

        temp = np.dot(data, [0.272, 0.534, 0.131])
        temp[temp > 255] = 255
        sepia[..., 2] = temp

        return Image.fromarray(sepia)

    def __grey_red(self, data):

        res1 = np.dot(data, [0.29, 0.58, 0.11])

        res = np.zeros_like(data)
        res[..., 0] = res1
        res[..., 1] = res1
        res[..., 2] = res1

        for x in range(data.shape[0]):
            for y in range(data.shape[1]):
                if data[x][y][0] > 150 and data[x][y][1] < 100 and data[x][y][2] < 100:
                    res[x][y] = data[x][y]
        return Image.fromarray(res)

    def __BLMethod(self, data):
        data = np.asarray(self.__grey(data))
        img = np.zeros_like(data)
        img[data > 128] = 255

        return Image.fromarray(img)
