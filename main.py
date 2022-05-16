import telebot
from telebot import types
import os
from PIL import Image, ImageEnhance, ImageFilter
import cv2

bot = telebot.TeleBot('5029443847:AAHkPxqK_6vBiD-89tiLWYpCz3D3s7ju4qI')

msg = ""
download_location = ""
edit_img_loc = ""

def dodgeV2(x, y):
    return cv2.divide(x, 255 - y, scale=256)

def download():
    img_id = list(msg.json.items())
    img_id = dict(img_id[4][1][len(img_id[4][1])-1])
    img_id = list(img_id.items())

    if not os.path.isdir(f"./DOWNLOADS"):
        os.makedirs(f"./DOWNLOADS")    
        if not os.path.isdir(f"./DOWNLOADS/{str(msg.chat.id)}"):
            os.makedirs(f"./DOWNLOADS/{str(msg.chat.id)}")

    file_info = bot.get_file(img_id[0][1])
    downloaded_file = bot.download_file(file_info.file_path)
    with open(download_location, 'wb') as new_file:
        new_file.write(downloaded_file)

def bright_0(call):
    bot.delete_message(msg.chat.id, call.message.message_id)
    bright_select = bot.send_message(msg.from_user.id, 'Введите число, где 0 - полностью черное изображение, 1 - исходная яркость')
    bot.register_next_step_handler(bright_select, bright_1, bright_select)

def bright_1(message, bright_select):
    bright_sel = message.text

    bot.delete_message(message.chat.id, bright_select.message_id)
    bot.delete_message(message.chat.id, message.message_id)

    download()

    image = Image.open(download_location)
    brightness = ImageEnhance.Brightness(image)
    brightness.enhance(float(bright_sel)).save(edit_img_loc)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))

def blur(call):
    bot.delete_message(msg.chat.id, call.message.message_id)

    keyboard_blur = types.InlineKeyboardMarkup()
    normal_blur = types.InlineKeyboardButton(text="Обычное размытие", callback_data="normal_blur")
    keyboard_blur.add(normal_blur)
    g_blur = types.InlineKeyboardButton(text="Гауссовское размытие", callback_data="g_blur")
    keyboard_blur.add(g_blur)
    box_blur = types.InlineKeyboardButton(text="Размытие в рамке", callback_data="box_blur")
    keyboard_blur.add(box_blur)
    bot.send_message(msg.chat.id, "Выберите режим", reply_markup=keyboard_blur)

def normal_blur(call):
    bot.delete_message(msg.chat.id, call.message.message_id)

    download()
    
    image = Image.open(download_location)
    blurImage = image.filter(ImageFilter.BLUR)
    blurImage.save(edit_img_loc)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))

def g_blur_0(call):
    bot.delete_message(msg.chat.id, call.message.message_id)
    power_select = bot.send_message(msg.from_user.id, 'Введите степень размытия')
    bot.register_next_step_handler(power_select, g_blur_1, power_select)

def g_blur_1(message, power_select):
    power_sel = message.text

    bot.delete_message(message.chat.id, power_select.message_id)
    bot.delete_message(message.chat.id, message.message_id)

    download()
    
    image = Image.open(download_location)
    g_blurImage = image.filter(ImageFilter.GaussianBlur(radius=float(power_sel)))
    g_blurImage.save(edit_img_loc)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))

def box_blur_0(call):
    bot.delete_message(msg.chat.id, call.message.message_id)
    power_select = bot.send_message(msg.from_user.id, 'Введите степень размытия')
    bot.register_next_step_handler(power_select, box_blur_1, power_select)
    
def box_blur_1(message, power_select):
    power_sel = message.text

    bot.delete_message(message.chat.id, power_select.message_id)
    bot.delete_message(message.chat.id, message.message_id)

    download()
    
    image = Image.open(download_location)
    box_blurImage = image.filter(ImageFilter.BoxBlur(float(power_sel)))
    box_blurImage.save(edit_img_loc)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))
    
def pencil(call):
    bot.delete_message(msg.chat.id, call.message.message_id)

    download()

    img = cv2.imread(download_location)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_invert = cv2.bitwise_not(img_gray)
    img_smoothing = cv2.GaussianBlur(img_invert, (21, 21), sigmaX=0, sigmaY=0)
    final_img = dodgeV2(img_gray, img_smoothing)
    cv2.imwrite(edit_img_loc, final_img)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))

def mix(call):
    bot.delete_message(msg.chat.id, call.message.message_id)

    download()

    image = Image.open(download_location)
    red, green, blue = image.split()
    new_image = Image.merge("RGB", (green, red, blue))
    new_image.save(edit_img_loc)

    bot.send_photo(msg.chat.id, photo = open(edit_img_loc, 'rb'))


@bot.message_handler(content_types=["photo"])
def any_msg(message):
    global msg, download_location, edit_img_loc
    msg = message
    download_location = "./DOWNLOADS" + "/" + str(msg.chat.id) + "/" + str(msg.chat.id) + ".jpg"
    edit_img_loc = "./DOWNLOADS" + "/" + str(msg.chat.id) + "/" + "file.jpg"

    keyboard = types.InlineKeyboardMarkup()
    bright = types.InlineKeyboardButton(text="Изменить яркость", callback_data="bright")
    keyboard.add(bright)
    blur = types.InlineKeyboardButton(text="Размытие", callback_data="blur")
    keyboard.add(blur)
    pencil = types.InlineKeyboardButton(text="Карандаш", callback_data="pencil")
    keyboard.add(pencil)
    mix = types.InlineKeyboardButton(text="Микс", callback_data="mix")
    keyboard.add(mix)
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "bright":
            bright_0(call)
        if call.data == "blur":
            blur(call)
        if call.data == "normal_blur":
            normal_blur(call)
        if call.data == "g_blur":
            g_blur_0(call)
        if call.data == "box_blur":
            box_blur_0(call)
        if call.data == "pencil":
            pencil(call)
        if call.data == "mix":
            mix(call)

if __name__ == '__main__':
    bot.infinity_polling()
