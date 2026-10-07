# Local Humanizer toolkit

This is a local, offline-first wrapper around `jialinyyzz/humanizer`. It uses Ollama directly and preserves the structured-file handling and quality checks from [`sgaofen/humanizer-local-model`](https://github.com/sgaofen/humanizer-local-model).

It supports pasted text, `.txt`, Markdown, `.docx`, and recursive folders. Outputs go to a new file or directory; input files are never overwritten.

## Installed commands

```bash
# Direct text
echo 'Paste or pipe text here.' | humanize

# Plain text or Markdown
humanize draft.txt -o draft.human.txt
humanize article.md -o article.human.md

# Microsoft Word
humanize report.docx -o report.human.docx

# A folder tree; existing outputs are skipped so interrupted jobs can resume
humanize-batch ./drafts ./humanized --report-dir ./reports
```

`humanize` auto-detects the first installed Ollama model whose name contains `humanizer`. To select one explicitly:

```bash
humanize draft.md -o draft.human.md \
  --ollama-model hf.co/jialinyyzz/humanizer:12b-IQ2_XS-QAT
```

Use `--json` to emit a report containing per-piece copy rates, missing or added numbers, missing URLs, retries, and flagged pieces:

```bash
humanize article.md -o article.human.md --json --quiet > article.report.json
```

Always read the output once, especially names, dates, numbers, and whether a claim became stronger or weaker. The automated checks cannot detect every change in meaning. No tool can guarantee an AI-detector result.

## What is preserved

Markdown headings, code blocks, tables, front matter, link-only lines, math blocks, block quotes, and reference sections are kept. Long prose is split into pieces and restored in place.

For DOCX, headings, tables, links, images, fields, equations, headers, footers, and reference sections are left alone. Rewritten paragraphs retain their paragraph style, but mixed bold or italic formatting inside one rewritten paragraph is lost because the whole paragraph takes the formatting of its first run.

## Set up on a home PC or any new computer

The toolkit needs Python 3.8 or newer, `pipx`, Ollama, and enough memory for the selected model. DOCX support uses the optional `python-docx` package. You do not need any extra Python package for plain text or Markdown.

### 1. Pre-installation checks

Windows PowerShell:

```powershell
py --version
ollama --version
git --version
nvidia-smi
```

Linux or macOS:

```bash
python3 --version
ollama --version
git --version
```

On Linux with an NVIDIA GPU, also run `nvidia-smi`. If Python, Git, Ollama, or the NVIDIA command is missing, install it before continuing. Update the NVIDIA driver if `nvidia-smi` cannot see the GPU.

Allow at least 12 GB of free disk space for this project, the Q4 model, and working files. The model itself is about 7.6 GB.

### 2. Get this project

Clone the Git repository, or copy this whole project folder to the new computer. Then open a terminal inside the folder containing `pyproject.toml`.

```bash
git clone YOUR_REPOSITORY_URL local-humanizer
cd local-humanizer
```

Replace `YOUR_REPOSITORY_URL` with the URL you publish this repository under. If you copied the directory manually, only the `cd` command is needed.

### 3. Pick and download a model

Choose one model. Do not download every size unless you want to compare them.

| Computer | Recommended model | Download size | Tradeoff |
| --- | --- | ---: | --- |
| RTX 3060 12 GB | `12b-Q4_K_M` | about 7.6 GB | Recommended balance of quality and speed |
| 12 GB shared memory or limited free VRAM | `12b-Q3-QAT` | about 5.6 GB | Lower memory use, with more possible fact slips |
| 8 GB memory or CPU-only testing | `12b-IQ2_XS-QAT` | about 3.9 GB | Smallest and fastest to load, but needs the most careful review |

For an RTX 3060 12 GB:

```bash
ollama pull hf.co/jialinyyzz/humanizer:12b-Q4_K_M
```

If Q4 reports an out-of-memory error:

```bash
ollama pull hf.co/jialinyyzz/humanizer:12b-Q3-QAT
```

For a low-memory or CPU-only computer:

```bash
ollama pull hf.co/jialinyyzz/humanizer:12b-IQ2_XS-QAT
```

Confirm the download:

```bash
ollama list
```

### 4. Install the commands

Windows PowerShell:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```

Close and reopen PowerShell after `ensurepath`, return to the project directory, and run:

```powershell
pipx install . --force
pipx inject humanize-model python-docx
```

Linux or macOS:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Open a new terminal if `pipx` is not immediately available, return to the project directory, and run:

```bash
pipx install . --force
pipx inject humanize-model python-docx
```

The `python-docx` injection is only required for `.docx` files, but installing it is harmless if you mainly use Markdown or text.

### 5. Verify the installation

```bash
humanize --version
humanize-batch --help
ollama list
```

The version command should print `hz 0.2.0-local`. Test a direct rewrite:

Windows PowerShell:

```powershell
"This solution serves as a testament to our commitment to innovation." | humanize
```

Linux or macOS:

```bash
echo 'This solution serves as a testament to our commitment to innovation.' | humanize
```

The first request can take longer while Ollama loads the model.

### 6. Confirm GPU acceleration

Start a rewrite, then check the model in another terminal:

```bash
ollama ps
nvidia-smi
```

For the RTX 3060, `ollama ps` should show `100% GPU` or mostly GPU. If it shows `100% CPU`, check the NVIDIA driver, restart Ollama, and run the test again. Keep only one large rewrite job active at a time because parallel requests compete for VRAM.

### 7. Select a model explicitly when necessary

Automatic detection uses the first installed Ollama model whose name contains `humanizer`. If several versions are installed, specify the intended model:

```bash
humanize article.md -o article.human.md \
  --ollama-model hf.co/jialinyyzz/humanizer:12b-Q4_K_M
```

PowerShell accepts the same command on one line:

```powershell
humanize article.md -o article.human.md --ollama-model hf.co/jialinyyzz/humanizer:12b-Q4_K_M
```

### 8. Upgrade or reinstall later

After pulling newer project files:

```bash
pipx install . --force
pipx inject humanize-model python-docx
```

Reinstalling with `--force` replaces the isolated command environment, so run the `pipx inject` command again for DOCX support.

## How it differs from the reference repository

The upstream `hz` command supports the Humanizer desktop app and llama.cpp. This local version adds Ollama as a native backend and a resumable recursive batch command. It still sends the model the exact raw completion prompt and evaluated sampler settings: temperature 1.0, top-p 0.95, top-k 0, min-p 0, repeat penalty 1.0, and no stop string.

The cloned upstream source is kept in `reference-humanizer-local-model/` for comparison. It is not required after this toolkit is installed.
