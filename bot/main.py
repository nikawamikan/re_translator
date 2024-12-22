from io import BytesIO
import discord
from discord import option
import aiohttp
from urllib.parse import quote
from aiocache import cached
from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_SOURCE_LANG = "ja"
DEFAULT_VIA_LANGS = "en,ko,ru,zh"
SOURCE_EMBED_COLOR = discord.Colour(0x12c4ff)
DESTINATION_EMBED_COLOR = discord.Colour(0xfd00ac)

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


def genelate_embed(title: str, description: str, color: discord.Colour):
    embed = discord.Embed(title=title, description=description)
    embed.colour = color
    return embed


def genelate_source_text_embed(text: str):
    return genelate_embed("再翻訳前", text, SOURCE_EMBED_COLOR)


def genelate_destination_text_embed(text: str):
    return genelate_embed("再翻訳後", text, DESTINATION_EMBED_COLOR)


@bot.slash_command(name="re_translate", description="逆翻訳します")
@option("text", description="翻訳するテキスト")
@option("source_lang", description="翻訳前の言語")
@option("via_langs", description="翻訳する言語 ex) en,ja")
async def re_translate(
    ctx: discord.ApplicationContext,
    text: str,
    source_lang: str = DEFAULT_SOURCE_LANG,
    via_langs: str = DEFAULT_VIA_LANGS,
):  # Takes one integer parameter
    await ctx.defer()

    try:
        translated_text = await translate_text(text, source_lang, via_langs)

        source_text_embed = genelate_source_text_embed(text)
        destination_text_embed = genelate_destination_text_embed(
            translated_text)
        await ctx.interaction.followup.send(embeds=[source_text_embed, destination_text_embed])
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
    source_lang: str = DEFAULT_SOURCE_LANG,
    via_langs: str = DEFAULT_VIA_LANGS,
):  # Takes one integer parameter
    await ctx.defer()

    try:
        translated_text = await translate_text(text, source_lang, via_langs)
        image = await text_to_image(translated_text)
        byteio = BytesIO(image)
        byteio.seek(0)
        source_text_embed = genelate_source_text_embed(text)
        await ctx.interaction.followup.send(embed=source_text_embed, file=discord.File(byteio, "translated_image.png"))
    except Exception as e:
        await ctx.interaction.followup.send("エラーが発生しました")
        raise e


@bot.message_command(name="re_translate", description="メッセージを逆翻訳します")
async def re_translate_message(ctx: discord.ApplicationContext, message: discord.Message):
    await ctx.defer()
    try:
        translated_text = await translate_text(message.content, DEFAULT_SOURCE_LANG, DEFAULT_VIA_LANGS)
        await ctx.followup.send(translated_text)
    except Exception:
        await ctx.followup.send("エラーが発生しました", ephemeral=True)
        raise

bot.run(TOKEN)
