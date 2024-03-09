import logging

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    ReplyKeyboardMarkup,
)

from pytube import YouTube

from utils import (
    youtube_download,
    instagram_download,
    reply_buttons,
    reply_back_button,
    update_users,
    checkAdmin,
    getAllUsers,
    getAllLinks,
    getWeeklyUsers,
    getMonthlyUsers,
    getWeeklyNewUsers,
    getMonthlyNewUsers,
    getAllAdmins,
    promoteToAdmin,
    removeAdmin,
    sendGlobalMessage,
    addLink,
)

import os

from constants import API_ID, API_HASH, BOT_TOKEN

logger = logging.getLogger(__name__)


users = {}
links = {}
qualities = {}
temp_message = dict()

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
def start_handler(client: Client, message: Message):
    logger.info(f"Bot started by {message.from_user.id}")

    update_users(message)

    global temp_message
    users[message.from_user.id] = "start"
    text = (
        "سلام خوش اومدی! \n من میتونم برات از اینستاگرام و یوتوب دانلود کنم😎 \n"
        " کافیه لینک ویدیوی یوتوب یا هر چیزی تو اینستا مثل استوری،پست، igtv و reel رو بفرستی تا فایلشو واست بفرستم🫡🤌"
    )
    reply_buttons(text, message, client)


@app.on_message(filters.command("adminpanel"))
def adminPanel(client: Client, message: Message):
    try:
        if not checkAdmin(message.chat.id):
            message.reply("only admins can use this command")

            logger.warn(f"{message.from_user.id} tried to access admin panel")
        else:
            #     temp_message[message.from_user.id] = message.reply_text(text="پنل ادمینی برای شما فعال شد", reply_markup=InlineKeyboardMarkup(
            # [
            #     [InlineKeyboardButton(text="اضافه کردن ادمین", callback_data="insta")],
            #     [InlineKeyboardButton(text="حذف ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            # ]
            # ))
            keyboard = ReplyKeyboardMarkup(
                [
                    ["تعداد تمام یوزر ها"],
                    ["تعداد یوزر های فعال هفته گذشته"],
                    ["تعداد یوزر های فعال ماه گذشته"],
                    ["تعداد یوزر های جدید هفته گذشته"],
                    ["تعداد یوزر های جدید ماه گذشته"],
                    ["لیست لینک های درخواستی"],
                    ["لیست ادمین ها"],
                    ["اضافه کردن ادمین"],
                    ["حذف ادمین"],
                    ["پیام همگانی"],
                    ["کنسل کردن درخواست"],
                ]
            )
            # client.send_message(message.from_user.id,"پنل ادمینی برای شما فعال شد" , reply_markup = keyboard,reply_to_message_id=message.id)
            message.reply("پنل ادمینی برای شما فعال شد", reply_markup=keyboard)
    except Exception as e:
        logger.error(e)


@app.on_callback_query()
def call_back_handler(client: Client, callback: CallbackQuery):
    global temp_message
    if callback.data == "youtube":
        try:
            temp_message[callback.message.chat.id].delete()
        except Exception:
            pass
        users[callback.from_user.id] = callback.data
        temp_message[callback.message.chat.id] = callback.message.reply_text(
            "لطفا لینک ویدیوی یوتوب رو بفرست🙏"
        )

    elif callback.data == "insta":
        try:
            temp_message[callback.message.chat.id].delete()
        except Exception:
            pass
        users[callback.from_user.id] = callback.data
        temp_message[callback.message.chat.id] = callback.message.reply_text(
            "لطفا لینک ویدیوی اینستاگرام رو بفرست🙏"
        )

    elif callback.data == "back":
        try:
            temp_message[callback.message.chat.id].delete()
        except Exception:
            pass
        users[callback.from_user.id] = ""
        text = "چه کار دیگه ای میتونم برات انجام بدم؟🤔"
        reply_buttons(text, callback.message, client)

    else:
        try:
            temp_message[callback.message.chat.id].delete()
        except Exception:
            pass
        ID = callback.from_user.id
        users[ID] = "download"

        title = youtube_download(
            link=links[ID], res=callback.data, message=callback.message, client=client
        )
        sent_message = callback.message.reply_text(
            "با موفقیت دانلود شد، در حال ارسال..."
        )

        special_characters = r'\/:*?"<>|#'
        path = (
            "".join(char for char in title if char not in special_characters) + ".mp4"
        )
        print(path)

        callback.message.reply_video(video=path)
        addLink(callback.message, "YouTube")
        sent_message.delete()

        reply_back_button(text="بازگشت؟", message=callback.message, client=client)

        os.remove(path=path)

        logger.info(f"{path} has been successfully deleted.")


@app.on_message(filters.text)
def message_handler(client: Client, message: Message):
    global temp_message

    update_users(message)

    if message.text == "تعداد تمام یوزر ها":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getAllUsers())
            text = "تعداد تمامی یوزر ها :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "لیست لینک های درخواستی":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            getAllLinks(message, client)
    elif message.text == "تعداد یوزر های فعال هفته گذشته":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getWeeklyUsers())
            text = "تعداد یوزر های فعال هفته گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "تعداد یوزر های فعال ماه گذشته":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyUsers())
            text = "تعداد یوزر های فعال ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "تعداد یوزر های جدید هفته گذشته":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getWeeklyNewUsers())
            text = "تعداد یوزر های جدید هفته گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "تعداد یوزر های جدید ماه گذشته":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyNewUsers())
            text = "تعداد یوزر های جدید ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "تعداد یوزر های جدید ماه گذشته":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyNewUsers())
            text = "تعداد یوزر های جدید ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif message.text == "لیست ادمین ها":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            text = getAllAdmins()
            message.reply(text)
    elif message.text == "اضافه کردن ادمین":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply("لطفا آی دی تلگرام کسی که می خواهید ادمین کنید را وارد کنید")
            users[message.from_user.id] = "addAdmin"
    elif message.text == "حذف ادمین":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply(
                "لطفا آی دی تلگرام کسی که می خواهید از ادمینی برکنار کنید را وارد کنید"
            )
            users[message.from_user.id] = "removeAdmin"
    elif message.text == "پیام همگانی":
        if not checkAdmin(message.from_user.id):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply("پیام بعدی شما به همه ی یوزر ها خواهد رفت")
            users[message.from_user.id] = "globalMessage"
    elif message.text == "کنسل کردن درخواست":
        users[message.from_user.id] = ""
    elif users[message.from_user.id] == "globalMessage":
        sendGlobalMessage(message, client)
        users[message.from_user.id] = ""
    elif users[message.from_user.id] == "addAdmin":
        promoteToAdmin(message, client)
        users[message.from_user.id] = ""
    elif users[message.from_user.id] == "removeAdmin":
        removeAdmin(message)
        users[message.from_user.id] = ""
    elif users[message.from_user.id] == "insta":
        try:
            temp_message[message.from_user.id].delete()
        except Exception:
            pass
        instagram_download(message.text, message, client)
        reply_back_button(text="بازگشت؟", message=message, client=client)

    elif users[message.from_user.id] == "youtube":
        if "youtube.com" in message.text or "youtu.be" in message.text:
            try:
                temp_message[message.from_user.id].delete()
            except Exception:
                pass
            video_url = message.text
            yt = YouTube(video_url)
            print("Available resolutions:")
            resolutions = []

            for stream in yt.streams.filter(progressive=True):
                print(stream.resolution)
                resolution_button = [
                    InlineKeyboardButton(
                        text=stream.resolution, callback_data=stream.resolution
                    )
                ]
                resolutions.append(resolution_button)

            txt = "یکی از کیفیت های موجود رو انتخاب کن. " + "\n"
            temp_message[message.from_user.id] = message.reply_text(
                text=txt, reply_markup=InlineKeyboardMarkup(resolutions)
            )

            users[message.from_user.id] = "ytquality"
            links[message.from_user.id] = message.text
            qualities[message.from_user.id] = resolutions

        else:
            text = "لینک اشتباه است، دوباره وارد کنید."
            text += "\n \n"
            text += "بازگشت؟"
            reply_buttons(text=text, message=message, client=client)
