

import os
import aiofiles
import aiohttp
import ffmpeg
import requests
from os import path
from asyncio.queues import QueueEmpty
from typing import Callable
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from rocks.cache.admins import set
from rocks.clientbot import clientbot, queues
from rocks.clientbot.clientbot import client as USER
from rocks.helpers.admins import get_administrators
from youtube_search import YoutubeSearch
from rocks import converter
from rocks.downloaders import youtube
from rocks.config import DURATION_LIMIT, que, SUDO_USERS
from rocks.config import BOT_NAME as bn
from rocks.config import ASSISTANT_NAME as an
from rocks.cache.admins import admins as a
from rocks.helpers.filters import command, other_filters
from rocks.helpers.command import commandpro
from rocks.helpers.decorators import errors, authorized_users_only
from rocks.helpers.errors import DurationLimitError
from rocks.helpers.gets import get_url, get_file_name
from PIL import Image, ImageFont, ImageDraw
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

# plus
chat_id = None
useer = "NaN"


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("resource/PicsArt_22-02-07_23-21-34-164.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    commandpro(["/play", "/yt", "/ytp", "play", "yt", "ytp", "@", "#"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    
    lel = await message.reply("**🔎 Sᴇᴀʀᴄʜɪɴɢ ...**")

    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "Alexa_Player"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "****")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**𝘐 𝘯𝘦𝘦𝘥 𝘈𝘥𝘮𝘪𝘯 𝘗𝘦𝘳𝘮𝘪𝘴𝘴𝘪𝘰𝘯 𝘵𝘰 𝘗𝘦𝘳𝘧𝘰𝘳𝘮 𝘵𝘩𝘪𝘴 𝘈𝘤𝘵𝘪𝘰𝘯...🤗**")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"**𝘗𝘭𝘦𝘢𝘴𝘦 𝘈𝘥𝘥 `{an}` 𝘔𝘢𝘯𝘶𝘢𝘭𝘭𝘺 𝘰𝘳 𝘊𝘰𝘯𝘵𝘢𝘤𝘵 : @readmeab ** ")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"**𝘗𝘭𝘦𝘢𝘴𝘦 𝘈𝘥𝘥 `{an}` 𝘔𝘢𝘯𝘶𝘢𝘭𝘭𝘺 𝘰𝘳 𝘊𝘰𝘯𝘵𝘢𝘤𝘵 : @readmeab ...*")
        return
    
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"**𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘌𝘳𝘳𝘰𝘳 : 𝘜𝘯𝘢𝘣𝘭𝘦 𝘵𝘰 𝘗𝘭𝘢𝘺 𝘚𝘰𝘯𝘨𝘴 𝘔𝘰𝘳𝘦 𝘛𝘩𝘢𝘯 {DURATION_LIMIT} 𝘔𝘪𝘯𝘶𝘵𝘦𝘴...**"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝘾𝙧𝙚𝙖𝙩𝙤𝙧", url=f"https://t.me/readmeab"),
                InlineKeyboardButton("𝙂𝙧𝙤𝙪𝙥", url=f"https://t.me/MovieDomes"),
            ]
        ]
    )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝘾𝙧𝙚𝙖𝙩𝙤𝙧", url=f"https://t.me/readmeab"),
                InlineKeyboardButton("𝙂𝙧𝙤𝙪𝙥", url=f"https://t.me/MovieDomes"),
            ]
        ]
    )

        except Exception as e:
            title = "NaN"
            thumb_name = "https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝘾𝙧𝙚𝙖𝙩𝙤𝙧", url=f"https://t.me/Telecat_X"),
                InlineKeyboardButton("𝙂𝙧𝙤𝙪𝙥", url=f"https://t.me/MovieDomes"),
            ]
        ]
    )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘌𝘳𝘳𝘰𝘳 : 𝘜𝘯𝘢𝘣𝘭𝘦 𝘵𝘰 𝘗𝘭𝘢𝘺 𝘚𝘰𝘯𝘨𝘴 𝘔𝘰𝘳𝘦 𝘛𝘩𝘢𝘯 {DURATION_LIMIT} 𝘔𝘪𝘯𝘶𝘵𝘦𝘴...**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "**🤔 𝘎𝘪𝘷𝘦 𝘔𝘦 𝘈 𝘚𝘰𝘯𝘨 𝘕𝘢𝘮𝘦 𝘰𝘳 𝘠𝘰𝘶𝘛𝘶𝘣𝘦 𝘓𝘪𝘯𝘬 𝘵𝘰 𝘗𝘭𝘢𝘺...**"
            )
        await lel.edit("**𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩 𝙄 𝙖𝙢 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "**𝘰𝘩-𝘚𝘯𝘢𝘱; 𝘚𝘰𝘯𝘨 𝘕𝘰𝘵 𝘍𝘰𝘶𝘯𝘥 𝘪𝘯 𝘠𝘰𝘶𝘛𝘶𝘣𝘦, 𝘛𝘳𝘺 𝘢𝘯𝘰𝘵𝘩𝘦𝘳 𝘰𝘯𝘦...**"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝘾𝙧𝙚𝙖𝙩𝙤𝙧", url=f"https://t.me/Telecat_X"),
                InlineKeyboardButton("𝙂𝙧𝙤𝙪𝙥", url=f"https://t.me/MovieDomes"),
            ]
        ]
    )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘌𝘳𝘳𝘰𝘳: 𝘜𝘯𝘢𝘣𝘭𝘦 𝘵𝘰 𝘗𝘭𝘢𝘺 𝘚𝘰𝘯𝘨𝘴 𝘔𝘰𝘳𝘦 𝘛𝘩𝘢𝘯 {DURATION_LIMIT} 𝘔𝘪𝘯𝘶𝘵𝘦𝘴...**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) in ACTV_CALLS:
        position = await queues.put(chat_id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption="**𝘚𝘰𝘯𝘨 𝘈𝘥𝘥𝘦𝘥 𝘵𝘰 𝘘𝘶𝘦𝘶𝘦 𝘢𝘵 𝘗𝘰𝘴𝘪𝘵𝘪𝘰𝘯 = `{}` ✅**".format(position),
            reply_markup=keyboard,
        )
    else:
        await clientbot.pytgcalls.join_group_call(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )

        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘋𝘪𝘳𝘦𝘤𝘵𝘭𝘺 𝘍𝘳𝘰𝘮 𝘠𝘰𝘶𝘛𝘶𝘣𝘦 𝘔𝘶𝘴𝘪𝘤...**".format(),
           )

    os.remove("final.png")
    return await lel.delete()
    
    
@Client.on_message(commandpro(["/pause", "pause"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    await clientbot.pytgcalls.pause_stream(message.chat.id)
    await message.reply_photo(
                             photo="https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png", 
                             caption="**𝘚𝘰𝘯𝘨 𝘪𝘴 𝘊𝘶𝘳𝘳𝘦𝘯𝘵𝘭𝘺 𝘗𝘢𝘶𝘴𝘦𝘥......**"
    )


@Client.on_message(commandpro(["/resume", "resume"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    await clientbot.pytgcalls.resume_stream(message.chat.id)
    await message.reply_photo(
                             photo="https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png", 
                             caption="**𝘚𝘰𝘯𝘨 𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘪𝘴 𝘙𝘦𝘴𝘶𝘮𝘦𝘥...**"
    )



@Client.on_message(commandpro(["/skip", "/next", "skip", "next"]) & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) not in ACTV_CALLS:
        await message.reply_text("**𝘚𝘰𝘯𝘨 𝘚𝘬𝘪𝘱𝘱𝘦𝘥 𝘵𝘰 𝘕𝘦𝘹𝘵...**")
    else:
        queues.task_done(chat_id)
        
        if queues.is_empty(chat_id):
            await clientbot.pytgcalls.leave_group_call(chat_id)
        else:
            await clientbot.pytgcalls.change_stream(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        clientbot.queues.get(chat_id)["file"],
                    ),
                ),
            )


    await message.reply_photo(
                             photo="https://telegra.ph/file/113b6e72f70c128f48abb.jpg", 
                             caption=f'**𝘚𝘰𝘯𝘨 𝘚𝘬𝘪𝘱𝘱𝘦𝘥 𝘵𝘰 𝘕𝘦𝘹𝘵...**'
   ) 


@Client.on_message(commandpro(["/end", "end", "/stop", "stop", "x"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
        clientbot.queues.clear(message.chat.id)
    except QueueEmpty:
        pass

    await clientbot.pytgcalls.leave_group_call(message.chat.id)
    await message.reply_photo(
                             photo="https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png", 
                             caption="**𝘚𝘰𝘯𝘨 𝘗𝘭𝘢𝘺𝘪𝘯𝘨 𝘚𝘵𝘰𝘱𝘱𝘦𝘥 𝘣𝘺 𝘺𝘰𝘶𝘳 𝘙𝘦𝘲𝘶𝘦𝘴𝘵...**"
    )


@Client.on_message(commandpro(["/reload", "reload", "refresh"]))
@errors
@authorized_users_only
async def admincache(client, message: Message):
    set(
        message.chat.id,
        (
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ),
    )

    await message.reply_photo(
                              photo="https://te.legra.ph/file/313e7bc8b8f8a3ebe28ed.png",
                              caption="**𝘙𝘦𝘭𝘰𝘢𝘥𝘦𝘥 𝘚𝘶𝘤𝘤𝘦𝘴𝘴𝘧𝘶𝘭𝘭𝘺...✅...**"
    )
