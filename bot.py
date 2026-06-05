import os
import discord
import json
import random
import asyncio
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
ID_CARGO_PRIMES = '1470900284644397217' 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# --- BANCO DE DADOS ---
ARQUIVO_DADOS = 'dados_primes.json'

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r') as f:
                return json.load(f)
        except: pass
    return {"jogadores": {}, "titulos": [], "partidas": [], "elenco_log": [], "aniversarios": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(dados, f, indent=4)

db = carregar_dados()

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f'Bot {bot.user} online! {len(synced)} comandos sincronizados.')

# --- SISTEMA DE BOTÕES (CONFIRMAÇÃO) ---
class ConfirmacaoPartida(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Vou", style=discord.ButtonStyle.green)
    async def vou(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.name} confirmou presença!", ephemeral=True)

# --- COMANDOS DE ESTATÍSTICAS ---
@bot.tree.command(name="perfil", description="Veja suas estatísticas ou de um jogador")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    alvo = usuario or interaction.user
    uid = str(alvo.id)
    if uid not in db["jogadores"]:
        db["jogadores"][uid] = {"nome": alvo.display_name, "gols": 0, "assist": 0, "saves": 0, "mvps": 0}
        salvar_dados(db)
    p = db["jogadores"][uid]
    embed = discord.Embed(title=f"👤 Perfil de {p['nome']}", color=discord.Color.green())
    embed.add_field(name="⚽ Gols", value=p['gols'], inline=True)
    embed.add_field(name="🎯 Assistências", value=p['assist'], inline=True)
    embed.add_field(name="🧤 Saves", value=p['saves'], inline=True)
    embed.add_field(name="🏆 MVPs", value=p.get('mvps', 0), inline=True)
    embed.set_thumbnail(url=alvo.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="atualizar-stats", description="Atualiza Gols, Assists ou Saves")
@app_commands.choices(categoria=[app_commands.Choice(name="Gols", value="gols"), app_commands.Choice(name="Assistências", value="assist"), app_commands.Choice(name="Saves", value="saves")])
async def atualizar_stats(interaction: discord.Interaction, jogador: discord.Member, categoria: app_commands.Choice[str], valor: int):
    uid = str(jogador.id)
    if uid not in db["jogadores"]:
        db["jogadores"][uid] = {"nome": jogador.display_name, "gols": 0, "assist": 0, "saves": 0, "mvps": 0}
    db["jogadores"][uid][categoria.value] = valor
    salvar_dados(db)
    await interaction.response.send_message(f"✅ {jogador.display_name}: {categoria.name} definido para {valor}.")

# --- RANKINGS ---
@bot.tree.command(name="ranking-geral", description="Visão geral de Gols, Assists, Saves e MVPs")
async def ranking_geral(interaction: discord.Interaction):
    jogadores = db["jogadores"]
    gols = sorted(jogadores.items(), key=lambda x: x[1].get("gols", 0), reverse=True)[:3]
    ast = sorted(jogadores.items(), key=lambda x: x[1].get("assist", 0), reverse=True)[:3]
    sav = sorted(jogadores.items(), key=lambda x: x[1].get("saves", 0), reverse=True)[:3]
    mvps = sorted(jogadores.items(), key=lambda x: x[1].get("mvps", 0), reverse=True)[:3]
    embed = discord.Embed(title="📊 RANKING GERAL - PRIMES FC", color=discord.Color.blue())
    embed.add_field(name="⚽ Top Gols", value="\n".join([f"{i+1}. {d[1]['nome']} ({d[1]['gols']})" for i, d in enumerate(gols)]) or "Nenhum", inline=True)
    embed.add_field(name="🎯 Top Assists", value="\n".join([f"{i+1}. {d[1]['nome']} ({d[1]['assist']})" for i, d in enumerate(ast)]) or "Nenhum", inline=True)
    embed.add_field(name="🧤 Top Saves", value="\n".join([f"{i+1}. {d[1]['nome']} ({d[1]['saves']})" for i, d in enumerate(sav)]) or "Nenhum", inline=True)
    embed.add_field(name="🏆 Top MVPs", value="\n".join([f"{i+1}. {d[1]['nome']} ({d[1].get('mvps', 0)})" for i, d in enumerate(mvps)]) or "Nenhum", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ranking-mvp", description="Ranking detalhado de MVPs")
async def ranking_mvp(interaction: discord.Interaction):
    jogadores = db["jogadores"]
    ranking = sorted(jogadores.items(), key=lambda x: x[1].get("mvps", 0), reverse=True)
    embed = discord.Embed(title="🏆 Tabela de MVPs - Primes FC", color=discord.Color.gold())
    texto = "\n".join([f"{i+1}º {d[1]['nome']}: {d[1].get('mvps', 0)} MVPs" for i, d in enumerate(ranking[:10])])
    embed.description = texto if texto else "Nenhum MVP registrado."
    await interaction.response.send_message(embed=embed)

# --- COMANDOS DE GESTÃO, TREINO E FERRAMENTAS ---
@bot.tree.command(name="treino", description="Inicia cronômetro de treino (ex: 60)")
async def treino(interaction: discord.Interaction, minutos: int):
    await interaction.response.send_message(f"⏱️ **Treino iniciado!** Duração: {minutos} minutos. Foco total, Primes!")
    await asyncio.sleep(minutos * 60)
    await interaction.channel.send(f"📢 **Fim do treino!** O tempo acabou, bom trabalho a todos.")

@bot.tree.command(name="sortear-times", description="Divide os membros presentes em 2 times")
async def sortear_times(interaction: discord.Interaction, canal: discord.VoiceChannel):
    membros = [m.display_name for m in canal.members]
    if len(membros) < 2:
        await interaction.response.send_message("❌ Precisa de pelo menos 2 pessoas no canal!")
        return
    random.shuffle(membros)
    meio = len(membros) // 2
    await interaction.response.send_message(f"⚽ **Sorteio:**\nTime A: {', '.join(membros[:meio])}\nTime B: {', '.join(membros[meio:])}")

@bot.tree.command(name="agendar-partida", description="Agenda uma partida com confirmação")
async def agendar(interaction: discord.Interaction, adversario: str, data_hora: str):
    embed = discord.Embed(title="⚽ Nova Partida Agendada", description=f"Adversário: {adversario}\nData/Hora: {data_hora}", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, view=ConfirmacaoPartida())

@bot.tree.command(name="resultado-partida", description="Registra e salva o resultado no histórico")
async def resultado(interaction: discord.Interaction, adversario: str, nosso_placar: int, placar_eles: int):
    res = "Vitória" if nosso_placar > placar_eles else ("Empate" if nosso_placar == placar_eles else "Derrota")
    db["partidas"].append(f"{res}: Primes FC {nosso_placar} x {placar_eles} {adversario}")
    salvar_dados(db)
    await interaction.response.send_message(f"✅ Partida registrada!")

@bot.tree.command(name="historico", description="Mostra o histórico de partidas")
async def historico(interaction: discord.Interaction):
    txt = "\n".join(db.get("partidas", [])[-10:])
    await interaction.response.send_message(f"📜 **HISTÓRICO DE JOGOS**\n{txt or 'Nenhuma partida registrada.'}")

@bot.tree.command(name="dica-tatica", description="Receba uma dica para o jogo")
async def dica_tatica(interaction: discord.Interaction):
    dicas = ["Mantenham a posse!", "Foco na marcação!", "Cubram as alas!", "Comunicação é tudo!", "Disciplina tática!"]
    await interaction.response.send_message(f"💡 **Dica Tática:** {random.choice(dicas)}")

@bot.tree.command(name="mvp", description="Define o destaque e adiciona 1 MVP")
async def mvp(interaction: discord.Interaction, jogador: discord.Member, motivo: str):
    uid = str(jogador.id)
    if uid not in db["jogadores"]:
        db["jogadores"][uid] = {"nome": jogador.display_name, "gols": 0, "assist": 0, "saves": 0, "mvps": 0}
    db["jogadores"][uid]["mvps"] = db["jogadores"][uid].get("mvps", 0) + 1
    salvar_dados(db)
    await interaction.response.send_message(f"🏆 {jogador.mention} é o MVP! Motivo: {motivo}")

@bot.tree.command(name="adicionar-titulo", description="Adiciona um troféu (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def adicionar_titulo(interaction: discord.Interaction, nome: str):
    db["titulos"].append(f"🏆 {nome}")
    salvar_dados(db)
    await interaction.response.send_message(f"✅ Título '{nome}' adicionado!")

@bot.tree.command(name="limpeza", description="Limpa mensagens (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def limpeza(interaction: discord.Interaction, quantidade: int):
    await interaction.channel.purge(limit=quantidade)
    await interaction.response.send_message("🧹 Limpeza concluída!", ephemeral=True)

bot.run(TOKEN)