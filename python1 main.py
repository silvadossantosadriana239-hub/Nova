# ############################################################################
# 🤖 BOT NOVA INTEL - VERSÃO PREMIUM COM ESTABILIZADOR ANTI-TRAVAMENTO
# ############################################################################

import requests
import re
import time
import json
import os
from datetime import datetime, timedelta

# ==============================================
# ⚙️ CONFIGURAÇÕES PRINCIPAIS
# ==============================================
TOKEN_TELEGRAM = "8674043088:AAFcjyrWMaC5SS7J8Skk_wgTcQyhPxid1sg"
TOKEN_API = "5f7d1c2d13742c61333112e0bd5e6fa2"
URL_BASE = "https://apis.gonzalesdev.shop/?token=" + TOKEN_API
URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}"

# ✅ SEU ID ATUALIZADO COMO ADMIN SUPREMO
SEU_USER_ID = 8289847251               

CHAVE_ATIVACAO_SISTEMA = "jm4179839@gmail.com"
LINK_SUPORTE_ATIVACAO = "https://t.me/jm_0752"
LINK_CANAL_OFICIAL = "https://t.me/grupooficialintel/1" 

DB_USUARIOS = "usuarios.txt"
DB_GRUPOS = "grupos.txt"

usuarios_com_plano = {}
sistema_pronto = True            
ultima_mensagem = {}  

sessao = requests.Session()

# ==============================================
# 📂 GERENCIADOR DE ARMAZENAMENTO E VÍNCULO DE USERS
# ==============================================
def salvar_id(arquivo, chat_id, username=""):
    chat_id = str(chat_id)
    if not os.path.exists(arquivo):
        with open(arquivo, "w", encoding="utf-8") as f: f.write("")
    
    with open(arquivo, "r", encoding="utf-8") as f:
        linhas = f.read().splitlines()
    
    encontrado = False
    novas_linhas = []
    
    for linha in linhas:
        if linha.startswith(chat_id + "|"):
            encontrado = True
            if username:
                novas_linhas.append(f"{chat_id}|{username.replace('@', '').strip().lower()}")
            else:
                novas_linhas.append(linha)
        else:
            novas_linhas.append(linha)
            
    if not encontrado:
        user_limpo = username.replace("@", "").strip().lower() if username else "sem_user"
        novas_linhas.append(f"{chat_id}|{user_limpo}")
        
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(novas_linhas) + "\n")

def buscar_id_por_username(username_alvo):
    user_procurado = username_alvo.replace("@", "").strip().lower()
    if os.path.exists(DB_USUARIOS):
        with open(DB_USUARIOS, "r", encoding="utf-8") as f:
            for linha in f.read().splitlines():
                if "|" in linha:
                    parts = linha.split("|")
                    if len(parts) >= 2 and parts[1] == user_procurado:
                        return int(parts[0])
    return None

def listar_ids(arquivo):
    if not os.path.exists(arquivo):
        return []
    ids = []
    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f.read().splitlines():
            if "|" in linha:
                ids.append(linha.split("|")[0])
            else:
                if linha.strip(): ids.append(linha.strip())
    return ids

# ==============================================
# 🔌 FUNÇÕES DE REQUISIÇÃO OTIMIZADAS
# ==============================================
def fazer_requisicao(metodo, dados=None):
    url = f"{URL_TELEGRAM}/{metodo}"
    timeout_req = 20 if metodo == "getUpdates" else 15
    for tentativa in range(3):
        try:
            res = sessao.post(url, json=dados, timeout=timeout_req)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            time.sleep(1)
    return {}

def enviar_documento_txt(destinatario_id, texto_conteudo, nome_arquivo="relatorio.txt"):
    try:
        url = f"{URL_TELEGRAM}/sendDocument"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(texto_conteudo)
        
        with open(nome_arquivo, "rb") as f:
            arquivos = {"document": f}
            dados = {"chat_id": destinatario_id}
            requests.post(url, data=dados, files=arquivos, timeout=30)
        
        if os.path.exists(nome_arquivo):
            os.remove(nome_arquivo)
    except Exception:
        pass

# ==============================================
# 🛡️ CONTROLE DE ACESSO E PLANOS
# ==============================================
def verificar_dono(usuario_id):
    return int(usuario_id) == int(SEU_USER_ID)

def verificar_plano_ativo(usuario_id):
    if verificar_dono(usuario_id):
        return True
    if int(usuario_id) not in usuarios_com_plano:
        return False
    data_expira = usuarios_com_plano[int(usuario_id)]
    return datetime.now() < data_expira

# ==============================================
# 🔍 MOTORES DE CONSULTA (APIs)
# ==============================================
def consultar_api_gonzales(rota, parametro, valor):
    try:
        valor_limpo = re.sub(r'[^a-zA-Z0-9./ ]', '', str(valor))
        url = f"{URL_BASE}&r={rota}&{parametro}={valor_limpo}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def consultar_cnpj_gratis(cnpj):
    try:
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        r = requests.get(f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}", timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def consultar_cep_gratis(cep):
    try:
        cep_limpo = re.sub(r'[^0-9]', '', cep)
        r = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}", timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def consultar_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,query", timeout=10)
        if r.status_code == 200:
            dados_ip = r.json()
            dados_api = consultar_api_gonzales("consulta_ip", "ip", ip)
            if dados_api and dados_api.get("dados"):
                dados_ip.update(dados_api["dados"])
            return dados_ip if dados_ip.get("status") == "success" else None
        return None
    except Exception:
        return None

def consultar_bin(bin_num):
    try:
        bin_limpo = re.sub(r'[^0-9]', '', bin_num)[:6]
        if len(bin_limpo) < 6: return None
        r = requests.get(f"https://lookup.binlist.net/{bin_limpo}", timeout=10, headers={"Accept-Version": "3"})
        if r.status_code == 200:
            dados_bin = r.json()
            dados_api = consultar_api_gonzales("consulta_bin", "bin", bin_limpo)
            if dados_api and dados_api.get("dados"):
                dados_bin.update(dados_api["dados"])
            return dados_bin
        return None
    except Exception:
        return None

def consultar_placa(placa):
    try:
        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
        if len(placa_limpa) < 7: return None
        dados = consultar_api_gonzales("consulta_placa", "placa", placa_limpa)
        if dados and dados.get("dados"):
            return dados["dados"]
        r = requests.get(f"https://api.placasbrasil.com.br/placa/{placa_limpa}", timeout=12)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

# ==============================================
# 🎨 FORMATADOR DINÂMICO RECURSIVO
# ==============================================
def processar_objeto_dinamico(objeto, prefixo=""):
    linhas_tele = []
    linhas_file = []
    
    if isinstance(objeto, str) and (objeto.strip().startswith("{") or objeto.strip().startswith("[")):
        try:
            objeto = json.loads(objeto)
        except Exception:
            pass

    if isinstance(objeto, dict):
        for chave, valor in objeto.items():
            if str(valor).strip() in ["", "None", "null", "[]", "{}"] or chave.upper() in ["OK", "ENCONTRADO"]:
                continue
            
            if isinstance(valor, (dict, list)) or (isinstance(valor, str) and (valor.strip().startswith("{") or valor.strip().startswith("["))):
                linhas_tele.append(f"\n📌 <b>--- {str(chave).upper()} ---</b>")
                linhas_file.append(f"\n--- {str(chave).upper()} ---\n")
                t_msg, t_file = processar_objeto_dinamico(valor, prefixo + "  ")
                linhas_tele.append(t_msg)
                linhas_file.append(t_file)
            else:
                linhas_tele.append(f"\n🔹 <b>{str(chave).upper()}:</b> <code>{str(valor)}</code>")
                linhas_file.append(f"{str(chave).upper()}: {str(valor)}\n")
                
    elif isinstance(objeto, list):
        for indice, item in enumerate(objeto):
            if isinstance(item, (dict, list)) or (isinstance(item, str) and (item.strip().startswith("{") or item.strip().startswith("["))):
                t_msg, t_file = processar_objeto_dinamico(item, prefixo)
                linhas_tele.append(t_msg)
                linhas_file.append(t_file)
            else:
                linhas_tele.append(f"\n🔸 <b>[{indice+1}]:</b> <code>{str(item)}</code>")
                linhas_file.append(f"[{indice+1}]: {str(item)}\n")
                
    return "".join(linhas_tele), "".join(linhas_file)

def gerar_lista_dados(dados, tipo_consulta, dado_original, usuario_id=None):
    if not dados:
        return f"❌ <b>NENHUM REGISTRO ENCONTRADO</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚠️ Sem resposta da API para: <code>{dado_original}</code>"

    if isinstance(dados, dict):
        if "dados" in dados and dados["dados"]: dados = dados["dados"]
        elif "resultado" in dados and dados["resultado"]: dados = dados["resultado"]

    emojis = {"sisreg": "⚡", "credilink": "📊", "cnh": "🪪", "pni": "🧬", "cred_tele": "📱", "nome": "👤", "cnpj": "🏢", "cep": "📍", "ip": "🌐", "bin": "💳", "placa": "🚗"}
    emoji = emojis.get(tipo_consulta, "✨")
    
    texto_base = f"{emoji} <b>NOVA INTEL | {tipo_consulta.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔍 <b>ALVO:</b> <code>{dado_original}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    texto_para_arquivo = f"RELATÓRIO NOVA INTEL - {tipo_consulta.upper()}\nALVO: {dado_original}\n" + "="*40 + "\n"

    conteudo_telegram, conteudo_arquivo = processar_objeto_dinamico(dados)
    
    texto_base += conteudo_telegram
    texto_para_arquivo += conteudo_arquivo

    texto_base += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏱️ <i>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y | %H:%M')}</i>\n🔐 <b>CONEXÃO CRIPTOGRAFADA</b>"
    texto_para_arquivo += "\n" + "="*40 + f"\nRelatório gerado em: {datetime.now().strftime('%d/%m/%Y | %H:%M')}"

    if usuario_id:
        enviar_documento_txt(usuario_id, texto_para_arquivo, f"Intel_{tipo_consulta}_{dado_original}.txt")

    return texto_base

# ==============================================
# 🎛️ GERENCIADOR DE TECLADOS (BOTÕES)
# ==============================================
def botoes_start_inicial():
    return {
        "inline_keyboard": [
            [{"text": "➕ Adicionar Bot no seu Grupo", "url": "https://t.me/jm_0752_bot?startgroup=true"}],
            [{"text": "📊 Abrir Painel de Consultas", "callback_data": "menu_grade_consultas"}],
            [{"text": "⚙️ Meu Plano", "callback_data": "meu_plano"}, {"text": "🆘 Ativação / Suporte", "url": LINK_SUPORTE_ATIVACAO}],
            [{"text": "📢 Canal Oficial Intel", "url": LINK_CANAL_OFICIAL}]
        ]
    }

def botoes_grade_consultas():
    return {
        "inline_keyboard": [
            [{"text": "🆔 Consultar CPF", "callback_data": "prompt_cpf"}, {"text": "🏢 Consultar CNPJ", "callback_data": "prompt_cnpj"}],
            [{"text": "📍 Consultar CEP", "callback_data": "prompt_cep"}],
            [{"text": "👤 Consultar Nome", "callback_data": "prompt_nome"}, {"text": "📱 Consultar Telefone", "callback_data": "prompt_tele"}],
            [{"text": "🚗 Consultar Placa", "callback_data": "prompt_placa"}],
            [{"text": "💳 Consultar BIN", "callback_data": "prompt_bin"}, {"text": "🌐 Consultar IP", "callback_data": "prompt_ip"}],
            [{"text": "🔙 Voltar ao Menu Principal", "callback_data": "voltar_para_start"}]
        ]
    }

def botoes_sub_bases_cpf(cpf):
    return {
        "inline_keyboard": [
            [{"text": "🩺 Base SISREG-III", "callback_data": f"lista:sisreg:{cpf}"}, {"text": "📊 Base Credilink", "callback_data": f"lista:credilink:{cpf}"}],
            [{"text": "🪪 Base CNH", "callback_data": f"lista:cnh:{cpf}"}, {"text": "🧬 Base SI-PNI", "callback_data": f"lista:pni:{cpf}"}],
            [{"text": "❌ Fechar Painel", "callback_data": "apagar_msg"}]
        ]
    }

def botoes_sub_bases_tele(tele):
    return {
        "inline_keyboard": [
            [{"text": "📊 Credilink Telefone", "callback_data": f"lista:cred_tele:{tele}"}],
            [{"text": "❌ Fechar Painel", "callback_data": "apagar_msg"}]
        ]
    }

def botoes_resultado_comum(tipo, dado):
    return {
        "inline_keyboard": [
            [{"text": "📄 Obter Relatório Completo", "callback_data": f"lista:{tipo}:{dado}"}],
            [{"text": "❌ Apagar Registro", "callback_data": "apagar_msg"}]]
    }

def botao_apagar_resultado():
    return {"inline_keyboard": [[{"text": "❌ Apagar Registro", "callback_data": "apagar_msg"}]]}

# ==============================================
# 🧠 CÉREBRO DE PROCESSAMENTO DE MENSAGENS
# ==============================================
def processar(chat_id, usuario_id, texto, msg_id=None, username_autor=""):
    global sistema_pronto

    texto = texto.strip()

    if int(chat_id) < 0:
        salvar_id(DB_GRUPOS, chat_id, username_autor)
    else:
        salvar_id(DB_USUARIOS, chat_id, username_autor)

    veio_de_botao = texto.startswith("BTN:")
    acao_limpa = texto.replace("BTN:", "") if veio_de_botao else texto

    if not sistema_pronto and not verificar_dono(usuario_id) and not any(texto.startswith(c) for c in ["/start", "/suporte", "/ativarsistema"]):
        fazer_requisicao("sendMessage", {
            "chat_id": chat_id, "text": "⚠️ <b>SISTEMA EM MANUTENÇÃO</b>\n\nAguarde a liberação do software.", "parse_mode": "HTML"
        })
        return

    # ==============================================
    # 📢 PAINEL DE TRANSMISSÃO AUTOMÁTICA
    # ==============================================
    if texto.startswith("/post_dm ") and verificar_dono(usuario_id):
        msg_enviar = texto.split(" ", 1)[1]
        lista_users = listar_ids(DB_USUARIOS)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🚀 <b>Iniciando envio para {len(lista_users)} usuários...</b>", "parse_mode": "HTML"})
        sucesso = 0
        for uid in lista_users:
            res = fazer_requisicao("sendMessage", {"chat_id": uid, "text": msg_enviar, "parse_mode": "HTML"})
            if res.get("ok"): sucesso += 1
            time.sleep(0.2)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"✅ <b>Envio Concluído!</b>\n📥 Entregue para: <code>{sucesso}/{len(lista_users)}</code> usuários.", "parse_mode": "HTML"})
        return

    elif texto.startswith("/post_grupos ") and verificar_dono(usuario_id):
        msg_enviar = texto.split(" ", 1)[1]
        lista_grupos = listar_ids(DB_GRUPOS)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🚀 <b>Iniciando envio para {len(lista_grupos)} grupos...</b>", "parse_mode": "HTML"})
        sucesso = 0
        for gid in lista_grupos:
            res = fazer_requisicao("sendMessage", {"chat_id": gid, "text": msg_enviar, "parse_mode": "HTML"})
            if res.get("ok"): sucesso += 1
            time.sleep(0.3)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"✅ <b>Envio Concluído!</b>\n📥 Entregue para: <code>{sucesso}/{len(lista_grupos)}</code> grupos.", "parse_mode": "HTML"})
        return

    elif texto.startswith("/post_geral ") and verificar_dono(usuario_id):
        msg_enviar = texto.split(" ", 1)[1]
        lista_all = listar_ids(DB_USUARIOS) + listar_ids(DB_GRUPOS)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🚀 <b>Disparando anúncio geral em {len(lista_all)} chats...</b>", "parse_mode": "HTML"})
        sucesso = 0
        for cid in lista_all:
            res = fazer_requisicao("sendMessage", {"chat_id": cid, "text": msg_enviar, "parse_mode": "HTML"})
            if res.get("ok"): sucesso += 1
            time.sleep(0.2)
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"✅ <b>Transmissão Concluída!</b>\n📥 Total: <code>{sucesso}/{len(lista_all)}</code>.", "parse_mode": "HTML"})
        return

    # ==============================================
    # 👑 COMANDOS DE ADMINISTRAÇÃO (DONO MASTER)
    # ==============================================
    if texto.startswith("/ativarsistema"):
        if not verificar_dono(usuario_id): return
        try:
            chave = texto.split(" ", 1)[1].strip()
            if chave == CHAVE_ATIVACAO_SISTEMA:
                sistema_pronto = True
                fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": "✅ <b>SISTEMA MASTER ONLINE!</b>", "parse_mode": "HTML"})
        except Exception: pass

    elif texto.startswith("/ativar "):
        if not verificar_dono(usuario_id): return
        try:
            partes = texto.split(" ")
            user_alvo, dias = partes[1], int(partes[2])
            id_alvo = buscar_id_por_username(user_alvo)
            
            if not id_alvo and user_alvo.isdigit():
                id_alvo = int(user_alvo)

            if id_alvo:
                data_expira = datetime.now() + timedelta(days=dias)
                usuarios_com_plano[int(id_alvo)] = data_expira
                fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"👑 <b>PLANO LICENCIADO!</b>\n\n👤 <b>Alvo:</b> {user_alvo}\n🆔 <b>ID Vinculado:</b> <code>{id_alvo}</code>\n📅 <b>Validade:</b> {dias} dias", "parse_mode": "HTML"})
            else:
                fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"❌ <b>@Username não encontrado na memória!</b>\n\n💡 <i>O usuário precisa dar /start no bot pelo menos uma vez antes de você ativá-lo por username!</i>", "parse_mode": "HTML"})
        except Exception: 
            fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": "⚠️ <b>Erro de sintaxe!</b> Use:\n<code>/ativar @username 30</code>", "parse_mode": "HTML"})

    elif texto.startswith("/remover "):
        if not verificar_dono(usuario_id): return
        try:
            user_alvo = texto.split(" ", 1)[1].strip()
            id_alvo = buscar_id_por_username(user_alvo)
            
            if not id_alvo and user_alvo.isdigit():
                id_alvo = int(user_alvo)
                
            if id_alvo and int(id_alvo) in usuarios_com_plano: 
                del usuarios_com_plano[int(id_alvo)]
                fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"❌ <b>Plano removido com sucesso para {user_alvo}!</b>", "parse_mode": "HTML"})
            else:
                fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ <b>Usuário {user_alvo} não possui plano ativo no sistema.</b>", "parse_mode": "HTML"})
        except Exception:
            fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": "⚠️ <b>Erro de sintaxe!</b> Use:\n<code>/remover @username</code>", "parse_mode": "HTML"})

    # ==============================================
    # ⚙️ INTERCEPTADOR DE EVENTOS DE BOTÕES
    # ==============================================
    elif veio_de_botao:
        if acao_limpa == "meu_plano":
            if verificar_dono(usuario_id):
                texto_plano = "👑 <b>PERFIL | ADMINISTRADOR SUPREMO</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ <b>Acesso:</b> Vitalício & Ilimitado"
            elif verificar_plano_ativo(usuario_id):
                data_exp = usuarios_com_plano[int(usuario_id)]
                texto_plano = f"⚙️ <b>MINHA CONTA</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ <b>Status:</b> Ativo\n📅 <b>Vence:</b> <code>{data_exp.strftime('%d/%m/%Y')}</code>"
            else:
                texto_plano = f"❌ <b>LICENÇA INATIVA</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👉 Adquira em: {LINK_SUPORTE_ATIVACAO}"

            fazer_requisicao("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id, "text": texto_plano, "parse_mode": "HTML",
                "reply_markup": {"inline_keyboard": [[{"text": "🔙 Voltar ao Painel", "callback_data": "voltar_para_start"}]]}
            })

        elif acao_limpa == "voltar_para_start":
            fazer_requisicao("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id,
                "text": "🤖 <b>PAINEL AUTOMATIZADO | NOVA INTEL</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 Selecione uma diretriz:",
                "parse_mode": "HTML", "reply_markup": botoes_start_inicial()
            })

        elif acao_limpa in ["menu_grade_consultas", "voltar_para_grade"]:
            fazer_requisicao("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id,
                "text": "📊 <b>BANCO DE FERRAMENTAS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nEscolha o módulo de busca que necessita:",
                "parse_mode": "HTML", "reply_markup": botoes_grade_consultas()
            })

        elif acao_limpa == "apagar_msg":
            fazer_requisicao("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

        elif acao_limpa.startswith("prompt_"):
            tipo = acao_limpa.split("_")[1]
            mensagens = {
                "cpf": "🆔 <b>MÓDULO CPF</b>\n\nEnvie:\n<code>/cpf seu_cpf</code>",
                "cnpj": "🏢 <b>MÓDULO CNPJ</b>\n\nEnvie:\n<code>/cnpj seu_cnpj</code>",
                "nome": "👤 <b>MÓDULO NOME</b>\n\nEnvie:\n<code>/nome NOME DO ALVO</code>",
                "tele": "📱 <b>MÓDULO TELEFONE</b>\n\nEnvie:\n<code>/tele seu_telefone</code>",
                "placa": "🚗 <b>MÓDULO PLACA</b>\n\nEnvie:\n<code>/placa sua_placa</code>",
                "cep": "📍 <b>MÓDULO CEP</b>\n\nEnvie:\n<code>/cep seu_cep</code>",
                "ip": "🌐 <b>MÓDULO IP</b>\n\nEnvie:\n<code>/ip seu_ip</code>",
                "bin": "💳 <b>MÓDULO BIN</b>\n\nEnvie:\n<code>/bin sua_bin</code>"
            }
            fazer_requisicao("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id, "text": mensagens.get(tipo, "Indisponível"), "parse_mode": "HTML",
                "reply_markup": {"inline_keyboard": [[{"text": "🔙 Módulos de Busca", "callback_data": "voltar_para_grade"}]]}
            })

        elif acao_limpa.startswith("lista:"):
            partes_lista = acao_limpa.split(":")
            tipo, dado = partes_lista[1], partes_lista[2]
            res = None
            if tipo in ["base_local", "sisreg", "cnh", "pni"]: res = consultar_api_gonzales("base_local", "cpf", dado)
            elif tipo == "credilink": res = consultar_api_gonzales("credilink", "cpf", dado)
            elif tipo == "cred_tele": res = consultar_api_gonzales("credilink", "telefone", dado)
            elif tipo == "nome": res = consultar_api_gonzales("base_local", "nome", dado)
            elif tipo == "cnpj": res = consultar_cnpj_gratis(dado)
            elif tipo == "cep": res = consultar_cep_gratis(dado)
            elif tipo == "ip": res = consultar_ip(dado)
            elif tipo == "bin": res = consultar_bin(dado)
            elif tipo == "placa": res = consultar_placa(dado)

            texto_resultado = gerar_lista_dados(res, tipo, dado, usuario_id=usuario_id)
            
            if int(chat_id) < 0:
                fazer_requisicao("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
                envio_dm = fazer_requisicao("sendMessage", {"chat_id": usuario_id, "text": texto_resultado, "parse_mode": "HTML", "reply_markup": botao_apagar_resultado()})
                
                if not envio_dm.get("ok"):
                    marcar = f"@{username_autor}" if username_autor else "Usuário"
                    fazer_requisicao("sendMessage", {
                        "chat_id": chat_id, 
                        "text": f"⚠️ {marcar}, <b>resultado bloqueado!</b>\nVocê precisa iniciar o bot no privado primeiro: @jm_0752_bot", 
                        "parse_mode": "HTML"
                    })
            else:
                fazer_requisicao("editMessageText", {
                    "chat_id": chat_id, "message_id": msg_id, "text": texto_resultado, "parse_mode": "HTML",
                    "reply_markup": botao_apagar_resultado()
                })

    # ==============================================
    # 👥 COMANDOS VIA TEXTO DIRETO (DM E GRUPOS)
    # ==============================================
    elif texto == "/suporte":
        fazer_requisicao("sendMessage", {
            "chat_id": chat_id, "text": f"🆘 <b>CENTRAL DE ATENDIMENTO</b>\n\nSuporte: {LINK_SUPORTE_ATIVACAO}", "parse_mode": "HTML"
        })

    elif texto.startswith("/start"):
        mensagem = "🤖 <b>PAINEL AUTOMATIZADO | NOVA INTEL</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎯 Respostas em alta velocidade e estabilidade."
        if not verificar_plano_ativo(usuario_id):
            mensagem += f"\n\n🛑 <b>CONTA BLOQUEADA:</b> Compre seu acesso na aba Suporte."
        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"{mensagem}\n\n👇 Escolha uma opção:", "parse_mode": "HTML", "reply_markup": botoes_start_inicial()})

    else:
        if not verificar_plano_ativo(usuario_id): return

        chat_destino = chat_id
        veio_do_grupo = int(chat_id) < 0
        
        if veio_do_grupo:
            chat_destino = usuario_id

        marcar = f"@{username_autor}" if username_autor else "Usuário"

        if texto.startswith("/cpf"):
            try:
                dado_limpo = re.sub(r'[^0-9]', '', texto.split(" ", 1)[1])
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"🆔 <b>ANÁLISE DE CPF:</b> <code>{dado_limpo}</code>", "parse_mode": "HTML", "reply_markup": botoes_sub_bases_cpf(dado_limpo)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/telefone") or texto.startswith("/tele"):
            try:
                dado_limpo = re.sub(r'[^0-9]', '', texto.split(" ", 1)[1])
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"📱 <b>ANÁLISE TELEFÔNICA:</b> <code>{dado_limpo}</code>", "parse_mode": "HTML", "reply_markup": botoes_sub_bases_tele(dado_limpo)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/nome "):
            try:
                dado = texto.split(" ", 1)[1]
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"👤 <b>ANÁLISE DE NOMINATIVO:</b> <code>{dado.upper()}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("nome", dado)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/cnpj "):
            try:
                dado_limpo = re.sub(r'[^0-9]', '', texto.split(" ", 1)[1])
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"🏢 <b>ANÁLISE EMPRESARIAL:</b> <code>{dado_limpo}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("cnpj", dado_limpo)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/cep "):
            try:
                dado_limpo = re.sub(r'[^0-9]', '', texto.split(" ", 1)[1])
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"📍 <b>ANÁLISE POSTAL:</b> <code>{dado_limpo}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("cep", dado_limpo)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/ip "):
            try:
                dado = texto.split(" ", 1)[1].strip()
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"🌐 <b>ANÁLISE DE IP:</b> <code>{dado}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("ip", dado)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/bin "):
            try:
                dado_limpo = re.sub(r'[^0-9]', '', texto.split(" ", 1)[1])[:6]
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"💳 <b>ANÁLISE DE BIN:</b> <code>{dado_limpo}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("bin", dado_limpo)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

        elif texto.startswith("/placa "):
            try:
                dado = texto.split(" ", 1)[1].upper()
                envio = fazer_requisicao("sendMessage", {"chat_id": chat_destino, "text": f"🚗 <b>ANÁLISE AUTOMOTIVA:</b> <code>{dado}</code>", "parse_mode": "HTML", "reply_markup": botoes_resultado_comum("placa", dado)})
                if veio_do_grupo:
                    if envio.get("ok"):
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"🔍 {marcar}, <b>consulta realizada! Abra sua DM.</b>", "parse_mode": "HTML"})
                    else:
                        fazer_requisicao("sendMessage", {"chat_id": chat_id, "text": f"⚠️ {marcar}, inicie o bot no privado primeiro clicando aqui: @jm_0752_bot", "parse_mode": "HTML"})
            except Exception: pass

# ==============================================
# 🔄 LOOP DE EXECUÇÃO ULTRA-ESTÁVEL (ANTI-QUEDA)
# ==============================================
def main():
    print("="*60)
    print("🤖 BOT INTEL MASTER OPERANTE - SISTEMA DE ALTA ESTABILIDADE")
    print("="*60)
    
    print("📥 Limpando buffer de mensagens acumuladas...")
    atualizacoes_iniciais = fazer_requisicao("getUpdates", {"offset": -1, "timeout": 1})
    ultimo_id = 0
    if atualizacoes_iniciais and "result" in atualizacoes_iniciais and len(atualizacoes_iniciais["result"]) > 0:
        ultimo_id = atualizacoes_iniciais["result"][0]["update_id"]
    print(f"✅ Buffer limpo! Iniciando monitoramento em tempo real.")

    while True:
        try:
            atualizacoes = fazer_requisicao("getUpdates", {"offset": ultimo_id + 1, "timeout": 25, "allowed_updates": ["message", "callback_query"]})
            if atualizacoes and "result" in atualizacoes:
                for upd in atualizacoes["result"]:
                    ultimo_id = upd["update_id"]
                    if "callback_query" in upd:
                        cbq = upd["callback_query"]
                        fazer_requisicao("answerCallbackQuery", {"callback_query_id": cbq["id"]})
                        username_autor = cbq["from"].get("username", "")
                        processar(cbq["message"]["chat"]["id"], cbq["from"]["id"], f"BTN:{cbq['data']}", cbq["message"]["message_id"], username_autor)
                    elif "message" in upd:
                        msg = upd["message"]
                        if "text" in msg: 
                            username_autor = msg["from"].get("username", "")
                            processar(msg["chat"]["id"], msg["from"]["id"], msg["text"], username_autor=username_autor)
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Instabilidade detectada: {e}. Reiniciando loop automático em 3 segundos...")
            time.sleep(3)

if __name__ == "__main__":
    main()
