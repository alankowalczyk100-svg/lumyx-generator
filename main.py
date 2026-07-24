import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

# =========================
# KONFIGURACJA
# =========================

TOKEN = os.getenv("TOKEN")

# ID kanału, na którym działa !gen
GEN_CHANNEL_ID = 123456789012345678  # <- tutaj wpisz ID swojego kanału

COOLDOWN_TIME = 7200  # 2 godziny w sekundach

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

cooldowns = {}

# =========================
# POMOCNICZE FUNKCJE
# =========================

def embed(title, description, color=0x8A2BE2):
    e = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    e.set_footer(text="Lumyx Generator")
    return e


def load_codes():
    try:
        with open("fortnite.txt", "r", encoding="utf-8") as f:
            return [x.strip() for x in f.readlines() if x.strip()]
    except:
        return []


def save_codes(codes):
    with open("fortnite.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(codes))


# =========================
# START BOTA
# =========================

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")


# =========================
# HELP
# =========================

@bot.command()
async def help(ctx):

    e = embed(
        "📚 Masz tu listę komend inwalido:",
        """
🎁 `!gen fortnite`
Losuje konto.

📦 `!stock`
Pokazuje ilość dostępnych kont.

🏓 `!ping`
Sprawdź se.

📚 `!help`
Pokazuje tę wiadomość.
"""
    )

    await ctx.send(embed=e)


# =========================
# STOCK
# =========================

@bot.command()
async def stock(ctx):

    codes = load_codes()

    await ctx.send(
        embed=embed(
            "📦 Stock",
            f"Pozostało **{len(codes)}** kont."
        )
    )


# =========================
# GENERATOR
# =========================

@bot.command()
async def gen(ctx, name=None):

    if name != "fortnite":
        return

    if ctx.channel.id != GEN_CHANNEL_ID:
        await ctx.send(
            embed=embed(
                "❌ Błąd",
                "Nie ten kanał krętaczu i oszuście.",
                0xff0000
            )
        )
        return


    user_id = ctx.author.id

    if user_id in cooldowns:

        left = cooldowns[user_id] - datetime.now()

        if left.total_seconds() > 0:

            hours = int(left.seconds // 3600)
            minutes = int((left.seconds % 3600) // 60)
            seconds = int(left.seconds % 60)

            await ctx.send(
                embed=embed(
                    "📦 Box! Stop!",
                    f"Czekaj kurwa, za **{hours}h {minutes}m {seconds}s** będziesz mógł generować.",
                    0xff9900
                )
            )
            return


    codes = load_codes()

    if len(codes) == 0:
        await ctx.send(
            embed=embed(
                "❌ Brak kont",
                "Aktualnie nie ma żadnych kont."
            )
        )
        return


    code = random.choice(codes)

    codes.remove(code)
    save_codes(codes)


    cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_TIME)


    try:

        await ctx.author.send(
            embed=embed(
                "🎁 Twoje konto Fortnite",
                f"Twoje konto:\n\n`{code}`\n\nMiłego używania!",
                0x00ff00
            )
        )

        await ctx.send(
            embed=embed(
                "✅ Wysłano!",
                "Sprawdź wiadomości prywatne."
            )
        )

    except:
        await ctx.send(
            embed=embed(
                "❌ Nie mogę wysłać PW",
                "Włącz prywatne wiadomości od serwera."
            )
        )


# =========================
# PING
# =========================

@bot.command()
async def ping(ctx):

    msg = await ctx.send(
        embed=embed(
            "🏓 Ping",
            "Kogo i na chuj chcesz pongować?"
        )
    )

    answers = [
        "To wypierdalaj.",
        "A wpierdol chcesz?",
        "Zamknij pizzę."
    ]


    def check(message):

        return (
            message.reference
            and message.reference.message_id == msg.id
            and message.author == ctx.author
        )


    try:

        reply = await bot.wait_for(
            "message",
            timeout=60,
            check=check
        )

        await reply.channel.send(
            embed=embed(
                "💀 Odpowiedź",
                random.choice(answers)
            )
        )

    except:
        pass



bot.run(TOKEN)
