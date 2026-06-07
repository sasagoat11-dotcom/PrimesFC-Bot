import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Carrega o token do arquivo .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Banco de dados de jogadores
db = {"partidas": [], "jogadores": {}}

def salvar_dados(db):
    pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot {bot.user} online! Comandos sincronizados.')

# --- COMANDOS DO PRIMES FC ---

@bot.tree.command(name="perfil", description="Mostra as estatísticas do seu perfil")
async def perfil(interaction: discord.Interaction, jogador: discord.Member = None):
    target = jogador or interaction.user
    uid = str(target.id)
    data = db["jogadores"].get(uid, {"gols": 0, "mvps": 0})
    
    embed = discord.Embed(title=f"👤 Perfil de {target.display_name}", color=discord.Color.gold())
    embed.add_field(name="⚽ Gols", value=data["gols"], inline=True)
    embed.add_field(name="🏆 MVPs", value=data["mvps"], inline=True)
    
    file = discord.File("primes fc icone.png", filename="icone.png")
    embed.set_thumbnail(url="attachment://icone.png")
    await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name="ranking", description="Mostra o ranking de gols do Primes FC")
async def ranking(interaction: discord.Interaction):
    # Ordena jogadores por gols
    sorted_players = sorted(db["jogadores"].items(), key=lambda x: x[1]["gols"], reverse=True)
    desc = "\n".join([f"{i+1}. {p[1].get('nome', 'Jogador')} - {p[1]['gols']} gols" for i, p in enumerate(sorted_players[:10])])
    
    embed = discord.Embed(title="📊 Ranking de Artilheiros - Primes FC", description=desc or "Nenhum dado ainda.", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="regras", description="Mostra as regras oficiais do Primes FC")
async def regras(interaction: discord.Interaction):
    regras_texto = (
        "**📜 REGRAS OFICIAIS — @Primes FC**\n\n"
        "**1. Identidade**: Time independente; proibido parcerias.\n"
        "**2. Comportamento**: Respeito obrigatório.\n"
        "**3. Compromisso**: Comparecer a treinos/partidas.\n"
        "**4. Hierarquia**: Respeitar decisões da liderança.\n"
        "**5. Avaliações**: Novos jogadores passam por avaliação.\n"
        "**6. Jogos**: Seriedade e respeito aos adversários.\n"
        "**7. Divulgação**: Proibido divulgar outros times.\n"
        "**8. Penalidades**: Advertências, afastamento ou remoção.\n"
        "**9. Disposições**: Regras podem ser atualizadas."
    )
    await interaction.response.send_message(regras_texto)

@bot.tree.command(name="escalacao", description="Cria a escalação oficial do Primes FC")
async def escalacao(interaction: discord.Interaction, goleiro: discord.Member, linha1: discord.Member, linha2: discord.Member, linha3: discord.Member):
    embed = discord.Embed(title="📋 ESCALAÇÃO OFICIAL - PRIMES FC", description="Aqui estão os titulares:", color=discord.Color.green())
    file = discord.File("primes fc icone.png", filename="icone.png")
    embed.set_thumbnail(url="attachment://icone.png")
    embed.add_field(name="🧤 GOLEIRO", value=f"**{goleiro.mention}**", inline=False)
    embed.add_field(name="⚽ JOGADORES DE LINHA", value=f"1. **{linha1.mention}**\n2. **{linha2.mention}**\n3. **{linha3.mention}**", inline=False)
    await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name="convocar", description="Convoca os jogadores para um compromisso")
async def convocar(interaction: discord.Interaction, cargo: discord.Role, motivo: str):
    embed = discord.Embed(title="📢 CONVOCAÇÃO - PRIMES FC", description=f"Atenção {cargo.mention}!\n\n**Motivo:** {motivo}", color=discord.Color.blue())
    file = discord.File("primes fc icone.png", filename="icone.png")
    embed.set_thumbnail(url="attachment://icone.png")
    await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name="historico", description="Mostra o histórico de partidas")
async def historico(interaction: discord.Interaction):
    txt = "\n".join(db.get("partidas", [])[-10:])
    await interaction.response.send_message(f"📜 **HISTÓRICO**\n{txt or 'Sem partidas recentes.'}")

@bot.tree.command(name="mvp", description="Define o destaque")
async def mvp(interaction: discord.Interaction, jogador: discord.Member):
    uid = str(jogador.id)
    if uid not in db["jogadores"]:
        db["jogadores"][uid] = {"nome": jogador.display_name, "gols": 0, "mvps": 0}
    db["jogadores"][uid]["mvps"] += 1
    salvar_dados(db)
    await interaction.response.send_message(f"🏆 {jogador.mention} é o MVP!")

@bot.tree.command(name="limpeza", description="Limpa mensagens (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def limpeza(interaction: discord.Interaction, quantidade: int):
    await interaction.channel.purge(limit=quantidade)
    await interaction.response.send_message("🧹 Limpeza feita!", ephemeral=True)

@bot.tree.command(name="gol", description="Registra um gol para um jogador")
async def gol(interaction: discord.Interaction, jogador: discord.Member):
    uid = str(jogador.id)
    if uid not in db["jogadores"]:
        db["jogadores"][uid] = {"nome": jogador.display_name, "gols": 0, "mvps": 0}
    db["jogadores"][uid]["gols"] += 1
    await interaction.response.send_message(f"⚽ Gol marcado para {jogador.display_name}!")

bot.run(TOKEN)
