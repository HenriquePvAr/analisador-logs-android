# =============================================================
# analisador.py
# Ferramenta de análise de logs Android
# Detecta crashes, ANRs, memory leaks e problemas de memória
# Agrupa por app, mostra linha do tempo e detecta recorrências
# Gera relatório colorido no terminal + arquivo .txt com data
# =============================================================

from colorama import init, Fore, Style
import os
import sys
from datetime import datetime

# collections: módulo padrão com estruturas de dados especiais
# defaultdict = dicionário que cria automaticamente um valor padrão
#               para chaves que ainda não existem
# Counter = conta quantas vezes cada item aparece numa lista
from collections import defaultdict, Counter

init(autoreset=True)


# =============================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================

EXPLICACOES_EXCECOES = {
    "NullPointerException":            "Código tentou usar um objeto que estava vazio (null). Verifique inicialização de variáveis.",
    "OutOfMemoryError":                "App esgotou a memória RAM disponível. Verifique vazamentos de memória (memory leak).",
    "IllegalStateException":           "Operação inválida no estado atual do app — comum ao manipular Fragments após onSaveInstanceState.",
    "IllegalArgumentException":        "Argumento inválido passado para um método — verifique os parâmetros da chamada.",
    "RuntimeException":                "Erro genérico em tempo de execução — leia o stack trace para identificar a causa raiz.",
    "IndexOutOfBoundsException":       "Acesso a uma posição inválida de lista ou array — índice fora dos limites.",
    "CursorIndexOutOfBoundsException": "Cursor de banco de dados apontou para uma linha que não existe — query retornou resultado vazio.",
    "SQLiteDiskIOException":           "Falha de I/O no banco de dados SQLite — disco cheio ou arquivo corrompido.",
    "ClassNotFoundException":          "Classe não encontrada em tempo de execução — dependência ausente ou ProGuard removeu a classe.",
    "ClassCastException":              "Tentativa de converter um objeto para um tipo incompatível.",
    "StackOverflowError":              "Recursão infinita ou muito profunda — método chamando a si mesmo sem condição de parada.",
    "NetworkOnMainThreadException":    "Operação de rede executada na thread principal — mova para uma thread separada (AsyncTask, Coroutine).",
    "SecurityException":               "Permissão negada — app tentou acessar recurso sem a permissão necessária no AndroidManifest.",
    "DeadObjectException":             "Tentativa de comunicação com um processo que já foi encerrado pelo Android.",
    "TransactionTooLargeException":    "Bundle ou Intent com dados grandes demais para o Binder — reduza o tamanho dos dados.",
}


# =============================================================
# PASSO 1: LER O ARQUIVO DE LOG
# =============================================================

def ler_log(caminho):
    """
    Abre o arquivo de log e retorna uma lista com cada linha.
    Verifica se o arquivo existe antes de tentar abrir.
    """
    if not os.path.exists(caminho):
        print(Fore.RED + f"\n❌ Arquivo não encontrado: '{caminho}'")
        print(Fore.YELLOW + "   Verifique se o arquivo está na mesma pasta que o analisador.py\n")
        sys.exit(1)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    print(Fore.CYAN + f"\n📂 Arquivo carregado: {caminho} ({len(linhas)} linhas)")
    return linhas


# =============================================================
# PASSO 2: CLASSIFICAR CADA LINHA POR NÍVEL DE LOG
# =============================================================

def classificar_linha(linha):
    """
    Identifica o nível de severidade de uma linha de log Android.

    Formato padrão do Logcat:
    MM-DD HH:MM:SS.mmm  PID  TID NIVEL TAG: mensagem
    ex: 03-20 10:00:01.001  800  820 E AndroidRuntime: FATAL EXCEPTION
    """
    partes = linha.split()

    if len(partes) >= 5:
        nivel = partes[4]
        if nivel == "E": return "ERROR"
        elif nivel == "W": return "WARNING"
        elif nivel == "I": return "INFO"
        elif nivel == "D": return "DEBUG"
        elif nivel == "V": return "VERBOSE"
        elif nivel == "F": return "FATAL"

    # fallback para logs com formato diferente
    if " E " in linha: return "ERROR"
    elif " W " in linha: return "WARNING"
    elif " I " in linha: return "INFO"
    elif " D " in linha: return "DEBUG"
    return "OUTRO"


# =============================================================
# PASSO 3: EXTRAIR TIMESTAMP DE UMA LINHA
# =============================================================

def extrair_timestamp(linha):
    """
    Extrai o timestamp de uma linha de log Android.

    Formato: "03-20 10:00:02.400  1400  1400 E ..."
    Retorna: "10:00:02.400" ou None se não encontrar

    Isso é usado para montar a linha do tempo dos eventos.
    """
    partes = linha.split()

    # um log válido começa com data (MM-DD) e hora (HH:MM:SS.mmm)
    # partes[0] = "03-20" | partes[1] = "10:00:02.400"
    if len(partes) >= 2:
        # verifica se partes[1] tem o formato de hora (contém ":")
        if ":" in partes[1]:
            return partes[1]  # retorna só a hora, ex: "10:00:02.400"

    return None


# =============================================================
# PASSO 4: EXTRAIR NOME DO APP/PROCESSO DE UMA LINHA
# =============================================================

def extrair_app(linha):
    """
    Tenta identificar o nome do app/processo numa linha de log.

    Estratégias:
    1. Procura "Process: com.xxx" (padrão de crash do AndroidRuntime)
    2. Procura "com.samsung." ou "com." no texto
    3. Retorna "sistema" se não encontrar nenhum app

    Isso é usado para agrupar problemas por app.
    """

    # estratégia 1: linha de crash tem "Process: com.pacote.app"
    # ex: "Process: com.samsung.camera, PID: 1400"
    if "Process:" in linha:
        return linha.split("Process:")[-1].split(",")[0].strip()

    # estratégia 2: procura qualquer pacote com formato "com.xxx.yyy"
    for palavra in linha.split():
        palavra_limpa = palavra.strip(",:()[]")
        if palavra_limpa.startswith("com.") and "." in palavra_limpa[4:]:
            return palavra_limpa

    # se não encontrou nenhum app, classifica como "sistema"
    return "sistema"


# =============================================================
# PASSO 5: DETECTAR PROBLEMAS E GERAR EXPLICAÇÕES
# =============================================================

def detectar_problemas(linhas):
    """
    Percorre todas as linhas procurando problemas críticos.
    Para cada problema, gera explicação, extrai timestamp e app.
    Retorna 4 listas: crashes, anrs, memoria, erros.
    """
    crashes = []
    anrs    = []
    memoria = []
    erros   = []

    for numero, linha in enumerate(linhas, start=1):
        linha = linha.strip()
        if not linha:
            continue

        # extrai timestamp e app de cada linha para usar nos eventos
        ts  = extrair_timestamp(linha)   # ex: "10:00:02.400"
        app = extrair_app(linha)         # ex: "com.samsung.camera"

        # -------------------------------------------------------
        # DETECÇÃO DE CRASHES
        # -------------------------------------------------------

        if "FATAL EXCEPTION" in linha:
            thread = linha.split("FATAL EXCEPTION:")[-1].strip() if "FATAL EXCEPTION:" in linha else "desconhecida"
            crashes.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app,
                "explicacao": f"App crashou na thread '{thread}' — processo encerrado pelo Android",
                "severidade": "CRITICO"
            })

        for excecao, explicacao in EXPLICACOES_EXCECOES.items():
            if excecao in linha:
                crashes.append({
                    "linha":      linha,
                    "numero":     numero,
                    "timestamp":  ts,
                    "app":        app,
                    "explicacao": explicacao,
                    "severidade": "CRITICO"
                })
                break

        # -------------------------------------------------------
        # DETECÇÃO DE ANR
        # -------------------------------------------------------

        if "ANR in" in linha:
            app_anr       = linha.split("ANR in")[-1].strip()
            nome_amigavel = app_anr.split(".")[-1] if "." in app_anr else app_anr
            anrs.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app_anr,
                "explicacao": f"App '{nome_amigavel}' ({app_anr}) não respondeu por +5s — Android exibiu diálogo 'App não está respondendo'",
                "severidade": "ALTO"
            })

        # -------------------------------------------------------
        # DETECÇÃO DE PROBLEMAS DE MEMÓRIA
        # -------------------------------------------------------

        if "Low memory condition detected" in linha:
            disponivel = linha.split("available=")[-1].split(" ")[0] if "available=" in linha else "desconhecida"
            limite     = linha.split("threshold=")[-1].split(" ")[0] if "threshold=" in linha else "desconhecido"
            memoria.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app,
                "explicacao": f"RAM baixa: {disponivel} disponível (limite: {limite}) — Android pode matar apps em background",
                "severidade": "MEDIO"
            })

        if "OutOfMemory condition" in linha:
            disponivel = linha.split("available=")[-1].strip() if "available=" in linha else "crítico"
            memoria.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app,
                "explicacao": f"Condição crítica de OOM: {disponivel} — sistema no limite, crash iminente",
                "severidade": "CRITICO"
            })

        if "Throwing OutOfMemoryError" in linha:
            memoria.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app,
                "explicacao": "Android lançou OutOfMemoryError — alocação de memória falhou completamente",
                "severidade": "CRITICO"
            })

        if "Storage critically low" in linha or "no space left on device" in linha:
            memoria.append({
                "linha":      linha,
                "numero":     numero,
                "timestamp":  ts,
                "app":        app,
                "explicacao": "Armazenamento interno crítico — pode causar falhas de escrita em banco de dados e logs",
                "severidade": "ALTO"
            })

        if classificar_linha(linha) == "ERROR":
            erros.append({"linha": linha, "numero": numero})

    return crashes, anrs, memoria, erros


# =============================================================
# PASSO 6: MONTAR LINHA DO TEMPO DOS EVENTOS
# =============================================================

def montar_linha_do_tempo(crashes, anrs, memoria):
    """
    Junta todos os eventos (crashes, ANRs, memória) numa lista única
    ordenada por timestamp, para mostrar a sequência de problemas.

    Isso ajuda a entender a causa raiz:
    ex: memória baixa às 10:00:02 → ANR às 10:00:04 → crash às 10:00:06
    Conclusão: a memória baixa provavelmente causou o ANR e o crash.
    """
    eventos = []

    for c in crashes:
        if c["timestamp"]:
            eventos.append({
                "timestamp": c["timestamp"],
                "tipo":      "CRASH",
                "app":       c["app"],
                "resumo":    c["linha"][:80] + "..." if len(c["linha"]) > 80 else c["linha"],
                "numero":    c["numero"]
            })

    for a in anrs:
        if a["timestamp"]:
            eventos.append({
                "timestamp": a["timestamp"],
                "tipo":      "ANR",
                "app":       a["app"],
                "resumo":    a["linha"][:80] + "..." if len(a["linha"]) > 80 else a["linha"],
                "numero":    a["numero"]
            })

    # adiciona alertas de memória crítica (só CRITICO para não poluir)
    for m in memoria:
        if m["timestamp"] and m["severidade"] == "CRITICO":
            eventos.append({
                "timestamp": m["timestamp"],
                "tipo":      "MEMORIA",
                "app":       m["app"],
                "resumo":    m["linha"][:80] + "..." if len(m["linha"]) > 80 else m["linha"],
                "numero":    m["numero"]
            })

    # sorted() ordena pelo timestamp — como é string HH:MM:SS.mmm,
    # ordenação alfabética funciona corretamente para ordenar por hora
    return sorted(eventos, key=lambda e: e["timestamp"] or "")


# =============================================================
# PASSO 7: AGRUPAR PROBLEMAS POR APP + DETECTAR RECORRÊNCIAS
# =============================================================

def agrupar_por_app(crashes, anrs):
    """
    Agrupa todos os crashes e ANRs por nome do app/processo.
    Detecta apps que tiveram mais de 1 problema (recorrência).
    Retorna dicionário ordenado pelo total de problemas.
    """
    grupos = defaultdict(lambda: {"crashes": [], "anrs": [], "total": 0, "recorrente": False})

    for c in crashes:
        grupos[c["app"]]["crashes"].append(c)
        grupos[c["app"]]["total"] += 1

    for a in anrs:
        grupos[a["app"]]["anrs"].append(a)
        grupos[a["app"]]["total"] += 1

    for app in grupos:
        if grupos[app]["total"] > 1:
            grupos[app]["recorrente"] = True

    # ordena pelo total de problemas — apps mais problemáticos primeiro
    return dict(sorted(grupos.items(), key=lambda item: item[1]["total"], reverse=True))


# =============================================================
# PASSO 8: GERAR ESTATÍSTICAS DO LOG
# =============================================================

def gerar_estatisticas(linhas):
    """
    Conta quantas linhas de cada nível existem no log.
    """
    stats = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0, "VERBOSE": 0, "FATAL": 0, "OUTRO": 0}
    for linha in linhas:
        stats[classificar_linha(linha.strip())] += 1
    return stats


# =============================================================
# PASSO 9: CONVERTER TIMESTAMP PARA SEGUNDOS
# =============================================================

def ts_para_segundos(ts):
    """
    Converte "HH:MM:SS.mmm" para segundos (float).
    Usado para calcular o intervalo entre eventos na linha do tempo.
    ex: "10:00:02.400" → 36002.4
    """
    partes = ts.split(":")
    if len(partes) == 3:
        return int(partes[0]) * 3600 + int(partes[1]) * 60 + float(partes[2])
    return 0


# =============================================================
# PASSO 10: EXIBIR RELATÓRIO COMPLETO NO TERMINAL
# =============================================================

def exibir_relatorio(linhas, crashes, anrs, memoria, erros):
    """
    Exibe o relatório completo no terminal com cores e formatação.
    """
    stats          = gerar_estatisticas(linhas)
    linha_do_tempo = montar_linha_do_tempo(crashes, anrs, memoria)
    grupos         = agrupar_por_app(crashes, anrs)

    # --- CABEÇALHO ---
    print("\n" + "="*65)
    print("         RELATÓRIO DE ANÁLISE DE LOG ANDROID")
    print("="*65)
    print(f"  Data  : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Linhas: {len(linhas)}")
    print("="*65)

    # --- ESTATÍSTICAS ---
    print(Fore.WHITE + "\n📊 DISTRIBUIÇÃO POR NÍVEL:")
    print(Fore.RED    + f"   ERROR   : {stats['ERROR']:>4} linhas")
    print(Fore.YELLOW + f"   WARNING : {stats['WARNING']:>4} linhas")
    print(Fore.CYAN   + f"   INFO    : {stats['INFO']:>4} linhas")
    print(Fore.WHITE  + f"   DEBUG   : {stats['DEBUG']:>4} linhas")

    # --- RESUMO EXECUTIVO ---
    total_criticos = len(crashes) + len(anrs)
    print(Fore.WHITE + f"\n🔍 RESUMO EXECUTIVO:")
    if total_criticos == 0:
        print(Fore.GREEN + "   ✅ Nenhum problema crítico detectado")
    else:
        print(Fore.RED    + f"   ⚠️  {total_criticos} problema(s) crítico(s) detectado(s)")
        print(Fore.RED    + f"      → {len(crashes)} crash(es)")
        print(Fore.YELLOW + f"      → {len(anrs)} ANR(s)")
        print(Fore.YELLOW + f"      → {len(memoria)} alerta(s) de memória")

    # --- TODAS AS LINHAS ---
    print("\n" + "-"*65)
    print("  LINHAS DO LOG")
    print("-"*65 + "\n")

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        tipo = classificar_linha(linha)
        if tipo == "ERROR":
            print(Fore.RED              + f"[ERROR]   {linha}")
        elif tipo == "WARNING":
            print(Fore.YELLOW           + f"[WARNING] {linha}")
        elif tipo == "INFO":
            print(Fore.CYAN             + f"[INFO]    {linha}")
        elif tipo == "DEBUG":
            print(Fore.WHITE            + f"[DEBUG]   {linha}")
        elif tipo == "FATAL":
            print(Fore.RED+Style.BRIGHT + f"[FATAL]   {linha}")
        else:
            print(                        f"[OUTRO]   {linha}")

    print("\n" + "="*65)
    print("              PROBLEMAS DETECTADOS")
    print("="*65)

    # -------------------------------------------------------
    # LINHA DO TEMPO
    # -------------------------------------------------------
    if linha_do_tempo:
        print(Fore.WHITE + f"\n⏱️  LINHA DO TEMPO ({len(linha_do_tempo)} evento(s) críticos):\n")

        cores  = {"CRASH": Fore.RED, "ANR": Fore.YELLOW, "MEMORIA": Fore.MAGENTA}
        icones = {"CRASH": "💥", "ANR": "🔒", "MEMORIA": "🧠"}

        evento_anterior = None
        for evento in linha_do_tempo:
            cor   = cores.get(evento["tipo"], Fore.WHITE)
            icone = icones.get(evento["tipo"], "•")

            intervalo = ""
            if evento_anterior and evento_anterior["timestamp"] and evento["timestamp"]:
                diff = ts_para_segundos(evento["timestamp"]) - ts_para_segundos(evento_anterior["timestamp"])
                if diff > 0:
                    intervalo = f"  (+{diff:.1f}s depois)"

            print(cor + f"   {icone} [{evento['timestamp']}] {evento['tipo']:<7} | Linha {evento['numero']:>3} | {evento['app']}{intervalo}")
            evento_anterior = evento
        print()

    # -------------------------------------------------------
    # AGRUPAMENTO POR APP COM DETECÇÃO DE RECORRÊNCIA
    # -------------------------------------------------------
    if grupos:
        print(Fore.WHITE + f"\n📱 PROBLEMAS POR APP ({len(grupos)} app(s) afetado(s)):\n")

        for app, dados in grupos.items():
            n_crashes = len(dados["crashes"])
            n_anrs    = len(dados["anrs"])

            if dados["recorrente"]:
                print(Fore.RED + Style.BRIGHT + f"   ⚠️  {app}  ← BUG RECORRENTE ({dados['total']} ocorrências)")
            else:
                print(Fore.YELLOW + f"   •  {app}")

            if n_crashes > 0:
                print(Fore.RED    + f"      💥 {n_crashes} crash(es)")
            if n_anrs > 0:
                print(Fore.YELLOW + f"      🔒 {n_anrs} ANR(s)")

            if dados["recorrente"]:
                todos = sorted(dados["crashes"] + dados["anrs"], key=lambda e: e["numero"])
                timestamps = [e["timestamp"] for e in todos if e["timestamp"]]
                if timestamps:
                    print(Fore.CYAN + f"      🕐 Ocorrências: {' → '.join(timestamps)}")
            print()

    # -------------------------------------------------------
    # LISTA DETALHADA DE CRASHES
    # -------------------------------------------------------
    if crashes:
        print(Fore.RED + f"\n🔴 CRASHES ({len(crashes)} ocorrência(s)):\n")
        for i, c in enumerate(crashes, start=1):
            print(Fore.RED    + f"  [{i}] Linha {c['numero']} | {c['timestamp'] or 'sem timestamp'} | {c['app']}")
            print(Fore.WHITE  + f"       {c['linha']}")
            print(Fore.YELLOW + f"       📌 {c['explicacao']}")
            print()
    else:
        print(Fore.GREEN + "\n✅ Nenhum crash encontrado")

    # -------------------------------------------------------
    # LISTA DETALHADA DE ANRs
    # -------------------------------------------------------
    if anrs:
        print(Fore.YELLOW + f"\n🟡 ANRs ({len(anrs)} ocorrência(s)):\n")
        for i, a in enumerate(anrs, start=1):
            print(Fore.YELLOW + f"  [{i}] Linha {a['numero']} | {a['timestamp'] or 'sem timestamp'} | {a['app']}")
            print(Fore.WHITE  + f"       {a['linha']}")
            print(Fore.CYAN   + f"       📌 {a['explicacao']}")
            print()
    else:
        print(Fore.GREEN + "\n✅ Nenhum ANR encontrado")

    # -------------------------------------------------------
    # LISTA DETALHADA DE MEMÓRIA
    # -------------------------------------------------------
    if memoria:
        print(Fore.YELLOW + f"\n⚠️  MEMÓRIA ({len(memoria)} ocorrência(s)):\n")
        for i, m in enumerate(memoria, start=1):
            cor = Fore.RED if m["severidade"] == "CRITICO" else Fore.YELLOW
            print(cor        + f"  [{i}] Linha {m['numero']} | {m['timestamp'] or 'sem timestamp'} | severidade: {m['severidade']}")
            print(Fore.WHITE + f"       {m['linha']}")
            print(Fore.CYAN  + f"       📌 {m['explicacao']}")
            print()
    else:
        print(Fore.GREEN + "\n✅ Sem problemas de memória")

    print("="*65)
    print("                    FIM DO RELATÓRIO")
    print("="*65 + "\n")


# =============================================================
# PASSO 11: SALVAR RELATÓRIO EM ARQUIVO .TXT
# =============================================================

def salvar_relatorio(linhas, crashes, anrs, memoria, caminho_log):
    """
    Salva o relatório completo com linha do tempo e agrupamento por app.
    """
    stats          = gerar_estatisticas(linhas)
    linha_do_tempo = montar_linha_do_tempo(crashes, anrs, memoria)
    grupos         = agrupar_por_app(crashes, anrs)

    agora        = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"relatorio_{agora}.txt"

    with open(nome_arquivo, "w", encoding="utf-8") as f:

        f.write("="*65 + "\n")
        f.write("         RELATÓRIO DE ANÁLISE DE LOG ANDROID\n")
        f.write("="*65 + "\n")
        f.write(f"  Arquivo analisado : {caminho_log}\n")
        f.write(f"  Data da análise   : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"  Total de linhas   : {len(linhas)}\n")
        f.write("="*65 + "\n")

        f.write("\n📊 DISTRIBUIÇÃO POR NÍVEL:\n")
        f.write(f"   ERROR   : {stats['ERROR']:>4} linhas\n")
        f.write(f"   WARNING : {stats['WARNING']:>4} linhas\n")
        f.write(f"   INFO    : {stats['INFO']:>4} linhas\n")
        f.write(f"   DEBUG   : {stats['DEBUG']:>4} linhas\n")

        total_criticos = len(crashes) + len(anrs)
        f.write(f"\n🔍 RESUMO EXECUTIVO:\n")
        if total_criticos == 0:
            f.write("   ✅ Nenhum problema crítico detectado\n")
        else:
            f.write(f"   ⚠️  {total_criticos} problema(s) crítico(s) detectado(s)\n")
            f.write(f"      → {len(crashes)} crash(es)\n")
            f.write(f"      → {len(anrs)} ANR(s)\n")
            f.write(f"      → {len(memoria)} alerta(s) de memória\n")

        if linha_do_tempo:
            f.write(f"\n{'='*65}\n")
            f.write(f"⏱️  LINHA DO TEMPO ({len(linha_do_tempo)} evento(s) críticos):\n\n")
            icones          = {"CRASH": "💥", "ANR": "🔒", "MEMORIA": "🧠"}
            evento_anterior = None
            for evento in linha_do_tempo:
                icone     = icones.get(evento["tipo"], "•")
                intervalo = ""
                if evento_anterior and evento_anterior["timestamp"] and evento["timestamp"]:
                    diff = ts_para_segundos(evento["timestamp"]) - ts_para_segundos(evento_anterior["timestamp"])
                    if diff > 0:
                        intervalo = f"  (+{diff:.1f}s depois)"
                f.write(f"   {icone} [{evento['timestamp']}] {evento['tipo']:<7} | Linha {evento['numero']:>3} | {evento['app']}{intervalo}\n")
                evento_anterior = evento

        if grupos:
            f.write(f"\n{'='*65}\n")
            f.write(f"📱 PROBLEMAS POR APP ({len(grupos)} app(s) afetado(s)):\n\n")
            for app, dados in grupos.items():
                recorrente = "⚠️  BUG RECORRENTE" if dados["recorrente"] else ""
                f.write(f"   • {app}  {recorrente}\n")
                f.write(f"     Crashes: {len(dados['crashes'])} | ANRs: {len(dados['anrs'])} | Total: {dados['total']}\n")
                if dados["recorrente"]:
                    todos = sorted(dados["crashes"] + dados["anrs"], key=lambda e: e["numero"])
                    timestamps = [e["timestamp"] for e in todos if e["timestamp"]]
                    if timestamps:
                        f.write(f"     Ocorrências: {' → '.join(timestamps)}\n")
                f.write("\n")

        f.write("="*65 + "\n")
        f.write("              PROBLEMAS DETALHADOS\n")
        f.write("="*65 + "\n")

        if crashes:
            f.write(f"\n🔴 CRASHES ({len(crashes)} ocorrência(s)):\n\n")
            for i, c in enumerate(crashes, start=1):
                f.write(f"  [{i}] Linha {c['numero']} | {c['timestamp'] or 'sem timestamp'} | {c['app']}\n")
                f.write(f"       {c['linha']}\n")
                f.write(f"       📌 {c['explicacao']}\n\n")
        else:
            f.write("\n✅ Nenhum crash encontrado\n")

        if anrs:
            f.write(f"\n🟡 ANRs ({len(anrs)} ocorrência(s)):\n\n")
            for i, a in enumerate(anrs, start=1):
                f.write(f"  [{i}] Linha {a['numero']} | {a['timestamp'] or 'sem timestamp'} | {a['app']}\n")
                f.write(f"       {a['linha']}\n")
                f.write(f"       📌 {a['explicacao']}\n\n")
        else:
            f.write("\n✅ Nenhum ANR encontrado\n")

        if memoria:
            f.write(f"\n⚠️  MEMÓRIA ({len(memoria)} ocorrência(s)):\n\n")
            for i, m in enumerate(memoria, start=1):
                f.write(f"  [{i}] Linha {m['numero']} | {m['timestamp'] or 'sem timestamp'} | severidade: {m['severidade']}\n")
                f.write(f"       {m['linha']}\n")
                f.write(f"       📌 {m['explicacao']}\n\n")
        else:
            f.write("\n✅ Sem problemas de memória\n")

        f.write("\n" + "="*65 + "\n")
        f.write("                   FIM DO RELATÓRIO\n")
        f.write("="*65 + "\n")

    print(Fore.GREEN + f"\n💾 Relatório salvo em: {nome_arquivo}\n")
    return nome_arquivo


# =============================================================
# PASSO 12: EXECUTAR TUDO
# =============================================================

if __name__ == "__main__":

    print(Fore.CYAN + Style.BRIGHT + """
╔══════════════════════════════════════════╗
║       ANALISADOR DE LOGS ANDROID        ║
╚══════════════════════════════════════════╝""")

    caminho = sys.argv[1] if len(sys.argv) > 1 else "log_sample.txt"

    linhas                        = ler_log(caminho)
    crashes, anrs, memoria, erros = detectar_problemas(linhas)
    exibir_relatorio(linhas, crashes, anrs, memoria, erros)
    salvar_relatorio(linhas, crashes, anrs, memoria, caminho)