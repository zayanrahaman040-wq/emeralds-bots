import discord
from discord.ext import commands
import os, aiohttp

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")

# ========== ROBLOX FOTO ==========
async def get_roblox_avatar(nome_roblox):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [nome_roblox], "excludeBannedUsers": False}) as r:
                data = await r.json()
                if not data.get("data"):
                    return None, None
                user_id = data["data"][0]["id"]
                username = data["data"][0]["name"]
            async with s.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false") as r2:
                data2 = await r2.json()
                url = data2["data"][0]["imageUrl"]
                return username, url
    except:
        return nome_roblox, None
    return nome_roblox, None

async def trova_log(guild):
    for nome in ["cc", "log-moderazione", "log-warn", "log-ban", "log-staff"]:
        ch = discord.utils.get(guild.channels, name=nome)
        if ch:
            return ch
    return None

# ========== MODAL BAN / WARN ==========
class ModModal(discord.ui.Modal):
    def __init__(self, tipo):
        super().__init__(title=f"{tipo} - Emeralds RP")
        self.tipo = tipo
        self.add_item(discord.ui.TextInput(label="Nome giocatore Roblox", placeholder="Es: Gigitopo17", required=True, max_length=50))
        self.add_item(discord.ui.TextInput(label="Motivazione", placeholder="Es: Cheat / Insulti / FailRP", required=True, style=discord.TextStyle.paragraph, max_length=500))
        self.add_item(discord.ui.TextInput(label="Vittima (se c'e')", placeholder="Nome vittima o Nessuna", required=False, max_length=50))

    async def on_submit(self, interaction: discord.Interaction):
        nome_roblox = self.children[0].value
        motivo = self.children[1].value
        vittima = self.children[2].value if len(self.children) > 2 and self.children[2].value else "Nessuna"
        
        await interaction.response.send_message(f"⏳ Sto inviando {self.tipo} per **{nome_roblox}**...", ephemeral=True)
        
        username, avatar = await get_roblox_avatar(nome_roblox)
        log = await trova_log(interaction.guild) or interaction.channel
        
        colore = 0xff0000 if self.tipo == "BAN" else 0xffa500
        emoji = "🔨" if self.tipo == "BAN" else "⚠️"
        
        embed = discord.Embed(title=f"{emoji} {self.tipo} - EMERALDS RP", color=colore)
        if avatar:
            embed.set_thumbnail(url=avatar)
        embed.add_field(name="🎮 Giocatore Roblox", value=f"**{username}**", inline=True)
        embed.add_field(name="👮 Operatore", value=interaction.user.mention, inline=True)
        embed.add_field(name="👤 Vittima", value=vittima, inline=True)
        embed.add_field(name="📝 Motivazione", value=motivo, inline=False)
        embed.set_footer(text=f"Emeralds RP • {self.tipo} da {interaction.user.name}")
        
        await log.send(embed=embed)
        await interaction.followup.send(f"✅ {self.tipo} inviato in {log.mention}!", ephemeral=True)

class ModView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="⚠️ WARN", style=discord.ButtonStyle.primary, custom_id="warn_btn")
    async def warn_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModModal("WARN"))
    @discord.ui.button(label="🔨 BAN", style=discord.ButtonStyle.red, custom_id="ban_btn")
    async def ban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModModal("BAN"))

@bot.command()
async def pannello_moderazione(ctx):
    embed = discord.Embed(title="🛡️ PANNELLO MODERAZIONE - EMERALDS RP", description="Clicca un bottone per aprire il form.\nCompila Nome Roblox + Motivazione e invia.", color=0xff0000)
    embed.add_field(name="⚠️ WARN", value="Warn con foto Roblox", inline=True)
    embed.add_field(name="🔨 BAN", value="Ban con foto Roblox", inline=True)
    await ctx.send(embed=embed, view=ModView())

# ========== PANNELLO TURNI (quello che hai già) ==========
class TurniView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🟢 Entra in servizio", style=discord.ButtonStyle.green, custom_id="entra")
    async def entra(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ {interaction.user.mention} è entrato in servizio!", ephemeral=False)
    @discord.ui.button(label="🔴 Fuori servizio", style=discord.ButtonStyle.red, custom_id="esci")
    async def esci(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"🔴 {interaction.user.mention} è uscito dal servizio!", ephemeral=False)

@bot.command()
async def pannello(ctx):
    embed = discord.Embed(title="EMERALS RP · Turni staff", description="Usa i bottoni per entrare / uscire dal servizio.", color=0x00ff00)
    await ctx.send(embed=embed, view=TurniView())

@bot.event
async def on_ready():
    bot.add_view(ModView())
    bot.add_view(TurniView())
    print(f"Online come {bot.user} - EMERALDS V2 PRONTO!")

bot.run(TOKEN)
