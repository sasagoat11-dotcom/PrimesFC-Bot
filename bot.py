import os
import discord
import json
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Configuração inicial
load_dotenv()
TOKEN = os.getenv('TOKEN')
ARQUIVO_DADOS = 'dados_primes.json'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(dados, f, indent=4)

@bot.event
async def on_ready():
    # Sincroniza os comandos de barra com o Discord
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s) de barra.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")
    print(f'Bot logado como {bot.user}')

# --- COMANDO DE BARRA /RESULT ---
@bot.tree.command(name="result", description="Registra o resultado de uma partida")
@app_commands.describe(
    adversario="Nome do time adversário",
    placar="Ex: 17-4",
    stats="Estatísticas (use \\n para quebrar linha)",
    mvp="Nome do MVP",
    runner_up="Nome do segundo colocado"
)
async def result(interaction: discord.Interaction, adversario: str, placar: str, stats: str, mvp: str, runner_up: str):
    # Formata o texto substituindo \n pelo caractere real de quebra de linha
    stats_formatado = stats.replace('\\n', '\n')
    
    mensagem = (
        f"🏆 **AMISTOSO — @Primes FC** ⚽\n\n"
        f"📟 **PLACAR**\n"
        f"Primes FC {placar} {adversario}\n\n"
        f"📊 **STATS**\n"
        f"{stats_formatado}\n\n"
        f"🥇 **MVP: {mvp}**\n"
        f"🥈 **RUNNER UP: {runner_up}**"
    )
    await interaction.response.send_message(mensagem)

# --- COLOQUE OUTROS COMANDOS ANTIGOS AQUI ABAIXO SE TIVER ---

# Iniciar o bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: Token não encontrado no Railway!")
