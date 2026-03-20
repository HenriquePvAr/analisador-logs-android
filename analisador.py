# analisador.py
# Ferramenta de análise de logs Android
# Detecta crashes, ANRs e problemas de memória automaticamente

# colorama é a biblioteca que deixa o terminal colorido
# init = inicializa a biblioteca
# Fore = controla a cor do texto
# Style = controla o estilo (negrito, etc)
from colorama import init, Fore, Style

# autoreset=True faz a cor voltar ao normal automaticamente depois de cada print
init(autoreset=True)


# ===============================================================
# PASSO 1: LER O ARQUIVO DE LOG
# ===============================================================

def ler_log(caminho):
    # "def" cria uma função — um bloco de código com nome que você pode chamar depois
    # "caminho" é o parâmetro — o endereço do arquivo que vamos abrir

    # "with open(...) as arquivo" abre o arquivo de forma segura
    # "r" = modo leitura (read)
    # "encoding utf-8" garante que caracteres especiais (ç, é, ã) funcionem
    with open(caminho, "r", encoding="utf-8") as arquivo:

        # readlines() lê o arquivo inteiro e retorna uma lista
        # cada posição da lista = uma linha do arquivo
        # ex: linhas[0] = primeira linha, linhas[1] = segunda linha
        linhas = arquivo.readlines()

    # "return" devolve o resultado da função para quem chamou ela
    return linhas


# ===============================================================
# PASSO 2: CLASSIFICAR CADA LINHA POR TIPO
# ===============================================================

def classificar_linha(linha):
    # essa função recebe uma linha de log e descobre o tipo dela
    # no log Android, o nível fica assim: ... 1234 E AndroidRuntime: ...
    # a letra isolada entre espaços ( E , W , I , D ) indica o nível

    # "in" verifica se um texto existe dentro de outro texto
    # ex: " E " in "1234 E AndroidRuntime" → True
    if " E " in linha:
        return "ERROR"      # erro grave, algo deu errado

    elif " W " in linha:
        return "WARNING"    # aviso, pode virar problema

    elif " I " in linha:
        return "INFO"       # informação normal do sistema

    elif " D " in linha:
        return "DEBUG"      # informação de desenvolvimento

    else:
        return "OUTRO"      # qualquer coisa que não se encaixou acima


# ===============================================================
# PASSO 3: DETECTAR PROBLEMAS GRAVES
# ===============================================================

def detectar_problemas(linhas):
    # essa função percorre todas as linhas e separa os problemas em listas

    crashes = []    # lista vazia que vai receber linhas de crash
    anrs = []       # lista vazia que vai receber linhas de ANR
    memoria = []    # lista vazia que vai receber linhas de memória
    erros = []      # lista vazia que vai receber todos os erros

    # "for linha in linhas" é um loop
    # ele pega uma linha por vez da lista e executa o bloco abaixo
    for linha in linhas:

        # strip() remove espaços em branco e \n (quebra de linha) do início e fim
        linha = linha.strip()

        # verifica se a linha contém "FATAL EXCEPTION"
        # se sim, adiciona na lista de crashes com .append()
        if "FATAL EXCEPTION" in linha:
            crashes.append(linha)

        # NullPointerException = tentou usar algo que era null (vazio)
        # "or" verifica as duas condições — basta uma ser verdadeira
        if "NullPointerException" in linha or "Exception" in linha:
            crashes.append(linha)

        # ANR = Application Not Responding (app travado por mais de 5 segundos)
        if "ANR in" in linha:
            anrs.append(linha)

        # Low memory = memória RAM baixa / OutOfMemory = ficou sem memória
        if "Low memory" in linha or "OutOfMemory" in linha:
            memoria.append(linha)

        # chama a função classificar_linha que fizemos antes
        # se ela retornar "ERROR", adiciona na lista de erros
        if classificar_linha(linha) == "ERROR":
            erros.append(linha)

    # retorna as 4 listas de uma vez
    # quem chamar essa função recebe tudo junto
    return crashes, anrs, memoria, erros


# ===============================================================
# PASSO 4: MOSTRAR O RELATÓRIO NO TERMINAL COM CORES
# ===============================================================

def exibir_relatorio(linhas, crashes, anrs, memoria, erros):
    # essa função recebe os resultados e exibe tudo formatado no terminal

    # "="*60 repete o caractere "=" 60 vezes — cria uma linha separadora
    print("\n" + "="*60)
    print("       RELATÓRIO DE ANÁLISE DE LOG ANDROID")
    print("="*60)

    # f"..." é uma f-string — permite colocar variáveis dentro do texto com {}
    # len(linhas) retorna o número de itens da lista (quantidade de linhas)
    print(f"\n📄 Total de linhas analisadas: {len(linhas)}")

    print("\n--- TODAS AS LINHAS ---\n")

    # loop que percorre cada linha e imprime com a cor certa
    for linha in linhas:
        linha = linha.strip()           # remove espaços e \n
        tipo = classificar_linha(linha) # descobre o tipo da linha

        # Fore.RED = texto vermelho, Fore.YELLOW = amarelo, etc
        # o texto entre aspas é formatado com o tipo e a linha original
        if tipo == "ERROR":
            print(Fore.RED    + f"[ERROR]   {linha}")
        elif tipo == "WARNING":
            print(Fore.YELLOW + f"[WARNING] {linha}")
        elif tipo == "INFO":
            print(Fore.CYAN   + f"[INFO]    {linha}")
        elif tipo == "DEBUG":
            print(Fore.WHITE  + f"[DEBUG]   {linha}")
        else:
            print(f"[OUTRO]   {linha}")

    # seção de resumo dos problemas
    print("\n" + "="*60)
    print("                    PROBLEMAS DETECTADOS")
    print("="*60)

    # "if crashes" verifica se a lista tem algum item
    # lista vazia = False, lista com itens = True
    if crashes:
        print(Fore.RED + f"\n🔴 CRASHES encontrados ({len(crashes)}):")
        for c in crashes:
            print(Fore.RED + f"   → {c}")
    else:
        print(Fore.GREEN + "\n✅ Nenhum crash encontrado")

    if anrs:
        print(Fore.YELLOW + f"\n🟡 ANRs encontrados ({len(anrs)}):")
        for a in anrs:
            print(Fore.YELLOW + f"   → {a}")
    else:
        print(Fore.GREEN + "\n✅ Nenhum ANR encontrado")

    if memoria:
        print(Fore.YELLOW + f"\n⚠️  Problemas de memória ({len(memoria)}):")
        for m in memoria:
            print(Fore.YELLOW + f"   → {m}")
    else:
        print(Fore.GREEN + "\n✅ Sem problemas de memória")

    print("\n" + "="*60)
    print("                      FIM DO RELATÓRIO")
    print("="*60 + "\n")


# ===============================================================
# PASSO 5: SALVAR RELATÓRIO EM ARQUIVO .TXT
# ===============================================================

def salvar_relatorio(linhas, crashes, anrs, memoria):
    # essa função salva o relatório num arquivo .txt com data e hora no nome
    # útil para guardar como evidência de teste ou enviar pro time

    # datetime é um módulo do Python que trabalha com datas e horas
    # importamos aqui dentro da função pois só usamos nela
    from datetime import datetime

    # .now() pega a data e hora atual
    # .strftime() formata a data no padrão que escolhemos
    # "%Y-%m-%d_%H-%M-%S" = ano-mês-dia_hora-minuto-segundo
    # ex: 2026-03-20_14-35-22
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # cria o nome do arquivo com a data no final
    # f-string junta o texto fixo com a variável agora
    nome_arquivo = f"relatorio_{agora}.txt"

    # abre (ou cria) o arquivo para escrita
    # "w" = modo escrita (write) — cria o arquivo se não existir
    with open(nome_arquivo, "w", encoding="utf-8") as f:

        # f.write() escreve texto no arquivo (igual print, mas no arquivo)
        # "\n" = quebra de linha
        f.write("="*60 + "\n")
        f.write("     RELATÓRIO DE ANÁLISE DE LOG ANDROID\n")
        f.write("="*60 + "\n")

        # registra quando o relatório foi gerado
        f.write(f"\nData da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de linhas analisadas: {len(linhas)}\n")

        f.write("\n--- PROBLEMAS DETECTADOS ---\n")

        # mesma lógica do exibir_relatorio, mas escrevendo no arquivo
        if crashes:
            f.write(f"\n🔴 CRASHES ({len(crashes)}):\n")
            for c in crashes:
                f.write(f"   → {c}\n")  # "\n" pula linha após cada item
        else:
            f.write("\n✅ Nenhum crash encontrado\n")

        if anrs:
            f.write(f"\n🟡 ANRs ({len(anrs)}):\n")
            for a in anrs:
                f.write(f"   → {a}\n")
        else:
            f.write("\n✅ Nenhum ANR encontrado\n")

        if memoria:
            f.write(f"\n⚠️  Memória ({len(memoria)}):\n")
            for m in memoria:
                f.write(f"   → {m}\n")
        else:
            f.write("\n✅ Sem problemas de memória\n")

        f.write("\n" + "="*60 + "\n")
        f.write("                   FIM DO RELATÓRIO\n")
        f.write("="*60 + "\n")

    # confirma no terminal que o arquivo foi salvo e mostra o nome
    print(Fore.GREEN + f"\n💾 Relatório salvo em: {nome_arquivo}")


# ===============================================================
# PASSO 6: EXECUTAR TUDO
# ===============================================================

# essa condição verifica se esse arquivo está sendo executado diretamente
# se outro arquivo importar esse, o bloco abaixo NÃO executa
# é uma boa prática em Python — evita rodar código acidentalmente
if __name__ == "__main__":

    # caminho do arquivo de log que vamos analisar
    # como está na mesma pasta, só precisamos do nome
    caminho = "log_sample.txt"

    # PASSO 1: lê o arquivo e guarda as linhas na variável
    linhas = ler_log(caminho)

    # PASSO 2 e 3: detecta os problemas e guarda nas 4 listas
    crashes, anrs, memoria, erros = detectar_problemas(linhas)

    # PASSO 4: exibe o relatório colorido no terminal
    exibir_relatorio(linhas, crashes, anrs, memoria, erros)

    # PASSO 5: salva o relatório em arquivo .txt com data e hora
    salvar_relatorio(linhas, crashes, anrs, memoria)