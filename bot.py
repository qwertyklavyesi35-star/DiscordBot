import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import sys
import requests


intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


DOSYA = "veri.json"


if os.path.exists(DOSYA):

    with open(DOSYA, "r", encoding="utf-8") as f:
        veri = json.load(f)

else:

    veri = {
        "aktif": False,
        "kanal": None,
        "kelimeler": [],
        "son_yazan": None,
        "skorlar": {}
    }



def kaydet():

    with open(DOSYA, "w", encoding="utf-8") as f:

        json.dump(
            veri,
            f,
            ensure_ascii=False,
            indent=4
        )




# KELİME KONTROL

def kelime_var_mi(kelime):

    try:

        url = f"https://sozluk.gov.tr/gts?ara={kelime}"

        cevap = requests.get(
            url,
            timeout=3
        )


        data = cevap.json()


        if isinstance(data, list):

            for item in data:

                if item.get("madde"):

                    return True



        return False



    except:

        return True





@bot.event
async def on_ready():

    print(f"{bot.user} aktif")

    await bot.tree.sync()

    print("Komutlar yüklendi")





# BAŞLAT


@bot.tree.command(
    name="kelimelik-baslat",
    description="Kelimelik başlat"
)

async def baslat(interaction: discord.Interaction):


    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Yetkin yok",
            ephemeral=True
        )

        return



    guild = interaction.guild


    kanal = discord.utils.get(
        guild.text_channels,
        name="kelimelik"
    )


    if kanal is None:

        kanal = await guild.create_text_channel(
            "kelimelik"
        )



    veri["aktif"] = True
    veri["kanal"] = kanal.id
    veri["kelimeler"] = []
    veri["son_yazan"] = None


    kaydet()



    await interaction.response.send_message(
        "✅ Kelimelik başladı!"
    )





# DURDUR


@bot.tree.command(
    name="kelimelik-durdur",
    description="Kelimeliği durdur"
)

async def durdur(interaction: discord.Interaction):


    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Yetkin yok",
            ephemeral=True
        )

        return



    veri["aktif"] = False

    kaydet()



    await interaction.response.send_message(
        "⛔ Kelimelik durduruldu"
    )





# SKOR SIFIRLA


@bot.tree.command(
    name="skor-sifirla",
    description="Skor sıfırlar"
)

async def sifirla(interaction: discord.Interaction):


    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Yetkin yok",
            ephemeral=True
        )

        return



    veri["skorlar"] = {}

    kaydet()



    await interaction.response.send_message(
        "♻️ Skorlar sıfırlandı"
    )





# SIRALAMA


@bot.tree.command(
    name="siralama",
    description="Sıralama"
)

async def siralama(interaction: discord.Interaction):


    if not veri["skorlar"]:

        await interaction.response.send_message(
            "Skor yok"
        )

        return



    liste = sorted(
        veri["skorlar"].items(),
        key=lambda x:x[1],
        reverse=True
    )


    mesaj = "🏆 Sıralama\n\n"


    for i,(id,puan) in enumerate(liste,1):

        user = await bot.fetch_user(int(id))

        mesaj += f"{i}. {user.name} - {puan} puan\n"



    await interaction.response.send_message(
        mesaj
    )





# RESTART


@bot.tree.command(
    name="restart",
    description="Bot restart"
)

async def restart(interaction: discord.Interaction):


    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ Yetkin yok",
            ephemeral=True
        )

        return



    await interaction.response.send_message(
        "🔄 Restart..."
    )


    await bot.close()


    os.execv(
        sys.executable,
        ["python"] + sys.argv
    )





# OYUN


@bot.event
async def on_message(message):


    if message.author.bot:
        return



    if message.channel.id != veri["kanal"]:

        await bot.process_commands(message)

        return



    if not veri["aktif"]:

        return



    kelime = message.content.lower().strip()



    if len(kelime) < 3:

        await message.delete()

        await message.channel.send(
            "❌ Geçerli kelime yaz",
            delete_after=3
        )

        return





    if not kelime_var_mi(kelime):

        await message.delete()

        await message.channel.send(
            "❌ Bu kelime bulunamadı!",
            delete_after=3
        )

        return





    if veri["son_yazan"] == message.author.id:


        await message.delete()


        await message.channel.send(
            "❌ Sıra sende değil!",
            delete_after=3
        )

        return





    if kelime in veri["kelimeler"]:


        await message.delete()


        await message.channel.send(
            "❌ Bu kelime daha önce yazıldı!",
            delete_after=3
        )

        return





    if veri["kelimeler"]:


        onceki = veri["kelimeler"][-1]


        if kelime[0] != onceki[-1]:


            await message.delete()


            await message.channel.send(
                f"❌ {onceki[-1].upper()} ile başlamalı!",
                delete_after=3
            )

            return





    veri["kelimeler"].append(kelime)

    veri["son_yazan"] = message.author.id



    uid = str(message.author.id)


    veri["skorlar"][uid] = veri["skorlar"].get(uid,0)+5


    kaydet()



    await message.add_reaction("✅")





bot.run("MTUyMTkzOTU2NDU3MzM2MDEzOA.GgujwY.t2l1JZq1OJzGExm3HPFQ52Qkn9LjjdE_wOtg0s")