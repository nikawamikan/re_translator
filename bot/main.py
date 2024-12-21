from io import BytesIO
import discord
from discord import option
import aiohttp
from urllib.parse import quote
from aiocache import cached
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set")


intents = discord.Intents.default()

bot = discord.Bot(intents=intents)


@cached(600)
async def translate_text(text: str, source_lang: str, via_langs: str) -> str:
    encoded_text = quote(text)
    encoded_source_lang = quote(source_lang)
    encoded_via_langs = quote(via_langs)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://127.0.0.1:8000/re_translate?text={encoded_text}&source_lang={
                encoded_source_lang}&via_langs={encoded_via_langs}"
        ) as response:
            translated_text = await response.text()

            # なんか前後に""がついてるので削除
            return translated_text


@cached(600)
async def text_to_image(text: str):
    escaped_text = quote(text)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://gsapi.cbrx.io/image?top={escaped_text}&single=true"
        ) as response:
            image = await response.read()

            return image


@bot.slash_command(name="re_translate", description="逆翻訳します")
@option("text", description="翻訳するテキスト")
@option("source_lang", description="翻訳前の言語")
@option("via_langs", description="翻訳する言語 ex) en,ja")
async def re_translate(
    ctx: discord.ApplicationContext,
    text: str,
    source_lang: str,
    via_langs: str,
):  # Takes one integer parameter
    await ctx.defer()

    try:
        translated_text = await translate_text(text, source_lang, via_langs)
        await ctx.interaction.followup.send(translated_text)
    except Exception as e:
        await ctx.interaction.followup.send("エラーが発生しました")
        raise e


@bot.slash_command(name="re_translate_image", description="逆翻訳して画像にします")
@option("text", description="翻訳するテキスト")
@option("source_lang", description="翻訳前の言語")
@option("via_langs", description="翻訳する言語 ex) en,ja")
async def re_translate_image(
    ctx: discord.ApplicationContext,
    text: str,
    source_lang: str,
    via_langs: str,
):  # Takes one integer parameter
    await ctx.defer()

    try:
        translated_text = await translate_text(text, source_lang, via_langs)
        image = await text_to_image(translated_text)
        byteio = BytesIO(image)
        byteio.seek(0)
        await ctx.interaction.followup.send(file=discord.File(byteio, "translated_image.png"))
    except Exception as e:
        await ctx.interaction.followup.send("エラーが発生しました")
        raise e

bot.run(TOKEN)
