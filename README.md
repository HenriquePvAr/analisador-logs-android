# 📱 Android Log Analyzer | Analisador de Logs Android

> 🇧🇷 Ferramenta em Python para análise automática de logs Android — detecta crashes, ANRs e problemas de memória.
>
> 🇺🇸 Python tool for automatic Android log analysis — detects crashes, ANRs and memory issues.

---

## 🇧🇷 Português

### Sobre o projeto

Ferramenta desenvolvida para auxiliar no processo de QA mobile. Lê arquivos de log gerados pelo Android (Logcat), classifica cada linha por nível de severidade e detecta automaticamente problemas críticos como crashes, ANRs e alertas de memória. Ao final, gera um relatório `.txt` com data e hora para uso como evidência de teste.

### Funcionalidades

- Leitura de arquivos de log do Android (Logcat)
- Classificação por nível: ERROR, WARNING, INFO, DEBUG
- Detecção automática de crashes (FATAL EXCEPTION, NullPointerException)
- Detecção automática de ANR (Application Not Responding)
- Detecção de problemas de memória (Low Memory, OutOfMemory)
- Exibição colorida no terminal
- Geração automática de relatório `.txt` com data e hora

### Tecnologias utilizadas

- Python 3
- colorama (cores no terminal)
- datetime (data e hora nos relatórios)

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

O relatório será salvo automaticamente na pasta com o nome `relatorio_YYYY-MM-DD_HH-MM-SS.txt`.

### Exemplo de saída

```
============================================================
       RELATÓRIO DE ANÁLISE DE LOG ANDROID
============================================================

📄 Total de linhas analisadas: 12

🔴 CRASHES encontrados (2):
   → E AndroidRuntime: FATAL EXCEPTION: main
   → E AndroidRuntime: java.lang.NullPointerException

🟡 ANRs encontrados (1):
   → I ActivityManager: ANR in com.samsung.gallery

⚠️  Problemas de memória (1):
   → W MemoryManager: Low memory condition detected

💾 Relatório salvo em: relatorio_2026-03-20_14-35-22.txt
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

A Python tool built to support the mobile QA process. It reads Android log files (Logcat), classifies each line by severity level, and automatically detects critical issues such as crashes, ANRs, and memory warnings. At the end, it generates a timestamped `.txt` report for use as test evidence.

### Features

- Reads Android Logcat log files
- Classifies lines by level: ERROR, WARNING, INFO, DEBUG
- Automatic crash detection (FATAL EXCEPTION, NullPointerException)
- Automatic ANR detection (Application Not Responding)
- Memory issue detection (Low Memory, OutOfMemory)
- Color-coded terminal output
- Automatic `.txt` report generation with timestamp

### Tech stack

- Python 3
- colorama (terminal colors)
- datetime (report timestamps)

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