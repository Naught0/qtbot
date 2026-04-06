import os

import discord
from discord.ext import commands


class Translate(commands.Cog):
    API_URL = "https://api.langbly.com/language/translate/v2"
    LANG_NAMES = {
        "af": "Afrikaans",
        "sq": "Albanian",
        "am": "Amharic",
        "ar": "Arabic",
        "hy": "Armenian",
        "az": "Azerbaijani",
        "eu": "Basque",
        "be": "Belarusian",
        "bn": "Bengali",
        "bs": "Bosnian",
        "bg": "Bulgarian",
        "ca": "Catalan",
        "zh": "Chinese",
        "hr": "Croatian",
        "cs": "Czech",
        "da": "Danish",
        "nl": "Dutch",
        "en": "English",
        "et": "Estonian",
        "fi": "Finnish",
        "fr": "French",
        "gl": "Galician",
        "ka": "Georgian",
        "de": "German",
        "el": "Greek",
        "gu": "Gujarati",
        "ht": "Haitian Creole",
        "he": "Hebrew",
        "hi": "Hindi",
        "hu": "Hungarian",
        "is": "Icelandic",
        "id": "Indonesian",
        "ga": "Irish",
        "it": "Italian",
        "ja": "Japanese",
        "kn": "Kannada",
        "kk": "Kazakh",
        "ko": "Korean",
        "lv": "Latvian",
        "lt": "Lithuanian",
        "mk": "Macedonian",
        "ms": "Malay",
        "ml": "Malayalam",
        "mt": "Maltese",
        "mr": "Marathi",
        "mn": "Mongolian",
        "no": "Norwegian",
        "fa": "Persian",
        "pl": "Polish",
        "pt": "Portuguese",
        "pa": "Punjabi",
        "ro": "Romanian",
        "ru": "Russian",
        "sr": "Serbian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "es": "Spanish",
        "sw": "Swahili",
        "sv": "Swedish",
        "ta": "Tamil",
        "te": "Telugu",
        "th": "Thai",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "ur": "Urdu",
        "vi": "Vietnamese",
        "cy": "Welsh",
    }

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.api_key = os.getenv("LANGBLY_API_KEY")

    @commands.command(name="translate", aliases=["tr", "tl"])
    async def _translate(self, ctx: commands.Context, *, text: str):
        """Translate auto-detected text to English

        Example: qt.translate Bonjour le monde"""
        if text is None or text.strip() == "":
            return await ctx.error("Give me some text to translate")

        if not self.api_key:
            return await ctx.error("Translation API key is not configured")

        payload = {
            "q": text,
            "target": "en",
            "translationMemory": True,
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        async with ctx.typing():
            resp = await self.session.post(
                self.API_URL,
                headers=headers,
                json=payload,
            )
            data = await resp.json()

        if data is None or "data" not in data:
            return await ctx.error("Translation failed, try again later")

        translation = data["data"]["translations"][0]
        translated_text = translation["translatedText"]
        detected = translation.get("detectedSourceLanguage", "unknown")
        lang_name = self.LANG_NAMES.get(detected, detected.title())

        em = discord.Embed(color=discord.Color.blurple())
        em.add_field(name=f"Detected: {lang_name}", value=text[:1024], inline=False)
        em.add_field(name="English", value=translated_text[:1024], inline=False)

        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Translate(bot))
