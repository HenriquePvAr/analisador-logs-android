# 📱 Android Log Analyzer | Analisador de Logs Android

> 🇧🇷 Ferramenta em Python para análise automática de logs Android — detecta crashes, ANRs, problemas de memória, agrupa por app e exibe linha do tempo dos eventos.
>
> 🇺🇸 Python tool for automatic Android log analysis — detects crashes, ANRs, memory issues, groups by app and displays a timeline of critical events.

---

## 🇧🇷 Português

### Sobre o projeto

Ferramenta desenvolvida para auxiliar no processo de QA mobile. Lê arquivos de log gerados pelo Android (Logcat), classifica cada linha por nível de severidade e detecta automaticamente problemas críticos como crashes, ANRs e alertas de memória.

Além de detectar os problemas, a ferramenta explica o que cada erro significa, agrupa os problemas por app, identifica bugs recorrentes e exibe uma linha do tempo mostrando a sequência dos eventos — o que ajuda a entender a causa raiz dos problemas.

Ao final, gera um relatório `.txt` com data e hora para uso como evidência de teste.

### Funcionalidades

- Leitura de arquivos de log do Android (Logcat)
- Classificação por nível: ERROR, WARNING, INFO, DEBUG, VERBOSE, FATAL
- Detecção automática de crashes com 15 tipos de exceção identificados
- Detecção automática de ANR (Application Not Responding)
- Detecção de problemas de memória RAM e armazenamento interno
- Explicação em português do que cada problema significa
- **Linha do tempo** dos eventos críticos com intervalo entre ocorrências
- **Agrupamento por app** com contagem de crashes e ANRs por processo
- **Detecção de bugs recorrentes** — apps com mais de uma ocorrência são destacados
- Estatísticas de distribuição por nível de log
- Resumo executivo com total de problemas críticos
- Exibição colorida no terminal
- Geração automática de relatório `.txt` com data e hora
- Suporte a arquivo customizado via argumento: `python analisador.py meu_log.txt`

### Tecnologias utilizadas

- Python 3
- colorama (cores no terminal)
- collections (agrupamento e contagem)
- datetime (data e hora nos relatórios)
- os / sys (verificação de arquivos e argumentos)

### Como executar

**1. Clone o repositório**

```bash
git clone https://github.com/HenriquePvAr/analisador-logs-android.git
cd analisador-logs-android
```

**2. Instale as dependências**

```bash
pip install -r requirements.txt
```

**3. Execute o analisador**

```bash
python analisador.py
```

Ou informe um arquivo de log específico:

```bash
python analisador.py meu_log.txt
```

O relatório será salvo automaticamente na pasta com o nome `relatorio_YYYY-MM-DD_HH-MM-SS.txt`.

### Exemplo de saída

```
=================================================================
         RELATÓRIO DE ANÁLISE DE LOG ANDROID
=================================================================
  Data  : 20/03/2026 16:01:59
  Linhas: 221

📊 DISTRIBUIÇÃO POR NÍVEL:
   ERROR   :   42 linhas
   WARNING :   31 linhas
   INFO    :   87 linhas
   DEBUG   :   61 linhas

🔍 RESUMO EXECUTIVO:
   ⚠️  14 problema(s) crítico(s) detectado(s)
      → 11 crash(es)
      → 3 ANR(s)
      → 10 alerta(s) de memória

⏱️  LINHA DO TEMPO (14 evento(s) críticos):

   💥 [10:00:02.400] CRASH   | Linha  48 | com.samsung.camera
   🔒 [10:00:04.300] ANR     | Linha  85 | com.samsung.gallery  (+1.9s depois)
   💥 [10:00:05.400] CRASH   | Linha 104 | com.samsung.settings (+1.1s depois)
   🔒 [10:00:06.300] ANR     | Linha 123 | com.samsung.messages (+0.9s depois)
   💥 [10:00:06.400] CRASH   | Linha 127 | com.samsung.messages (+0.1s depois)

📱 PROBLEMAS POR APP (5 app(s) afetado(s)):

   ⚠️  com.samsung.messages  ← BUG RECORRENTE (2 ocorrências)
      🔒 1 ANR(s)
      💥 1 crash(es)
      🕐 Ocorrências: 10:00:06.300 → 10:00:06.400

   •  com.samsung.camera
      💥 2 crash(es)

🔴 CRASHES (11 ocorrência(s)):

  [1] Linha 48 | 10:00:02.400 | com.samsung.camera
      E AndroidRuntime: FATAL EXCEPTION: main
      📌 App crashou na thread 'main' — processo encerrado pelo Android

💾 Relatório salvo em: relatorio_2026-03-20_16-01-59.txt
```

### Estrutura do projeto

```
analisador-logs-android/
│
├── analisador.py       # script principal
├── log_sample.txt      # exemplo de log Android para teste
├── requirements.txt    # dependências do projeto
└── README.md           # documentação
```

---

## 🇺🇸 English

### About

A Python tool built to support the mobile QA process. It reads Android log files (Logcat), classifies each line by severity level, and automatically detects critical issues such as crashes, ANRs, and memory warnings.

Beyond detection, the tool explains what each error means, groups issues by app, identifies recurring bugs, and displays a timeline showing the sequence of events — making it easier to identify root causes.

At the end, it generates a timestamped `.txt` report for use as test evidence.

### Features

- Reads Android Logcat log files
- Classifies lines by level: ERROR, WARNING, INFO, DEBUG, VERBOSE, FATAL
- Automatic crash detection with 15 identified exception types
- Automatic ANR detection (Application Not Responding)
- RAM and internal storage issue detection
- Plain-language explanation of what each problem means
- **Event timeline** with time intervals between occurrences
- **Grouping by app** with crash and ANR count per process
- **Recurring bug detection** — apps with multiple issues are highlighted
- Log level distribution statistics
- Executive summary with total critical issues
- Color-coded terminal output
- Automatic `.txt` report generation with timestamp
- Custom log file support: `python analisador.py my_log.txt`

### Tech stack

- Python 3
- colorama (terminal colors)
- collections (grouping and counting)
- datetime (report timestamps)
- os / sys (file verification and arguments)

### How to run

**1. Clone the repository**

```bash
git clone https://github.com/HenriquePvAr/analisador-logs-android.git
cd analisador-logs-android
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the analyzer**

```bash
python analisador.py
```

Or pass a custom log file:

```bash
python analisador.py my_log.txt
```

The report will be saved automatically as `relatorio_YYYY-MM-DD_HH-MM-SS.txt`.

### Project structure

```
analisador-logs-android/
│
├── analisador.py       # main script
├── log_sample.txt      # sample Android log for testing
├── requirements.txt    # project dependencies
└── README.md           # documentation
```

---

## ✍️ Author | Autor

Feito por / Made by **Henrique Araujo**

Estudante de QA Mobile | Mobile QA Student

[![GitHub](https://img.shields.io/badge/GitHub-black?style=flat&logo=github)](https://github.com/HenriquePvAr)