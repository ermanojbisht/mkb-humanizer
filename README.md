# Local Humanizer

Rewrite text and documents locally with Ollama and the
[`jialinyyzz/humanizer`](https://huggingface.co/jialinyyzz/humanizer) model.
Choose the **PySide6 desktop app** with its blue glass-style interface, or the
**command line** for individual files and recursive folders.

Supported inputs: pasted text, `.txt`, Markdown (`.md`), and Word (`.docx`).
The GUI and CLI share the same rewriting engine and quality checks.

## What you need

- **Python:** use Python 3.10 or newer for a new installation. The core CLI declares
  Python 3.8+ support, but GUI and DOCX dependencies have their own version requirements.
- **pipx:** installs the toolkit in its own Python environment; no activation needed.
- **Git:** to clone/update the repository. Downloading the repository ZIP is also possible.
- **Ollama:** runs the model separately from the Python app.
- **Memory and disk:** the Q4 model is about 7.6 GB on disk. Allow additional space for
  Ollama, Python dependencies, and output files. Model runtime memory exceeds its
  download size; a 12 GB GPU is a useful starting point for Q4, but available VRAM,
  context size, and other applications affect whether it fits. CPU inference is possible
  but can be slower. Smaller variants are listed on the model page.

Internet access is needed to install dependencies and download the model. With a local
Ollama server and the model already installed, rewriting works offline.
The GUI needs a graphical desktop session.

**Platform status:** the GUI and CLI have been verified on Linux. Windows instructions
are provided below, but the GUI has not yet been tested on Windows.

## 1. Install prerequisites

### Linux (Ubuntu / Debian)

On a distribution with Python 3.10 or newer:

```bash
sudo apt update
sudo apt install python3 python3-venv pipx git
pipx ensurepath
```

Close and reopen the terminal after `ensurepath`. On other distributions, install
Python, pipx, and Git through your distribution's package manager; see the
[pipx installation guide](https://pipx.pypa.io/).

Install Ollama using the [official Linux instructions](https://docs.ollama.com/linux).
The standard installation command is:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify:

```bash
python3 --version
pipx --version
git --version
ollama --version
```

If `ollama list` cannot connect, start Ollama. For a systemd service installation:

```bash
sudo systemctl start ollama
```

If Ollama was installed without a service, run `ollama serve` in a separate terminal
and leave it running. If Ollama is already running, do not start a second server.

### Windows (PowerShell)

Install [Python](https://www.python.org/downloads/windows/) (Python 3.12 is a suitable
choice), [Git](https://git-scm.com/downloads/win), and
[Ollama for Windows](https://ollama.com/download/windows). Start the Ollama application;
it normally runs in the background. See the [official Windows guide](https://docs.ollama.com/windows).

Open PowerShell and install pipx:

```powershell
py --version
py -m pip install --user pipx
py -m pipx ensurepath
```

Close and reopen PowerShell, then verify:

```powershell
pipx --version
git --version
ollama --version
ollama list
```

If `pipx` still is not found, use `py -m pipx` in place of `pipx` in the commands below.

## 2. Get this repository

Run these commands in Linux's terminal or Windows PowerShell:

```text
git clone https://github.com/ermanojbisht/mkb-humanizer.git
cd mkb-humanizer
```

If you downloaded a ZIP or copied the project folder, open a terminal inside the
extracted folder containing `pyproject.toml` instead. Copy the source files, not an
existing pipx environment or only the `humanize-gui` launcher. Install fresh on each PC.

## 3. Install the GUI, CLI, or both

Run **one** of the following inside the repository folder. Single quotes work in
both Linux shells and PowerShell.

| What you want | Install command | Available commands |
| --- | --- | --- |
| Desktop app plus CLI, including Word support | `pipx install '.[gui]'` | `humanize-gui`, `humanize`, `humanize-batch`, `hz` |
| CLI with Word support | `pipx install '.[docx]'` | `humanize`, `humanize-batch`, `hz` |
| CLI for text and Markdown only | `pipx install .` | `humanize`, `humanize-batch`, `hz` |

**Recommended for most users:** `pipx install '.[gui]'`. It includes PySide6 and
`python-docx`; a separate `pipx inject` is unnecessary.

If the toolkit is already installed, add `--force` to install the chosen option:

```text
pipx install '.[gui]' --force
```

Pipx manages the environment and puts its launchers on your PATH. `pipx list` shows
where they are installed. On this project's Linux development machine, the environment
is `~/.local/pipx/venvs/humanize-model/`; other pipx versions or operating systems may
use different paths. The package name is **humanize-model**, and the app name is
**MKB Humanizer**. The Ollama model is stored separately.

## 4. Download or select the model

On either operating system:

```text
ollama pull hf.co/jialinyyzz/humanizer:Q4_K_M
ollama list
```

If that exact model is already listed, skip the download. The toolkit asks Ollama
for its installed models; it does not search arbitrary Hugging Face cache folders.

Use the **exact name and tag shown by `ollama list`**. `Q4_K_M` is the working tag
used in these examples. Do not download another copy just because an older guide
uses a different tag. For smaller variants, consult the
[model author's size and quality table](https://huggingface.co/jialinyyzz/humanizer).

The CLI selects the first installed model whose name contains `humanizer` unless
one is specified. The GUI lists installed names containing `humanizer` and remembers
your selection. A model does not need to be loaded before you start; Ollama loads it
on the first rewrite, which can take longer.

This toolkit uses Humanizer's specific raw completion prompt. The CLI can accept
another model name, but it does not adapt that model's chat template; arbitrary
Ollama chat models are not currently supported by the GUI.

## 5. Use the desktop app

Launch from a terminal or PowerShell:

```text
humanize-gui
```

1. Check the Ollama address, normally `http://127.0.0.1:11434`, and click **Refresh**.
2. Select your installed Humanizer model.
3. In **Text studio**, paste text or Markdown into **Original draft** and click **Humanize**.
4. Review **Refined result** and **Activity & quality checks**, then **Copy** or **Save text…**.
5. For a file, use **Documents**, browse for the input, choose a separate output with
   the same extension, and click **Humanize**.
6. Use **Export report** to save the JSON quality report after a successful rewrite.

The window stays responsive while rewriting and shows elapsed time. **Cancel** stops
the local rewrite process. Document results are staged separately and published only
after success; cancellation or generation failure leaves existing output files intact.
Ollama may briefly continue processing an already submitted request after cancellation.
Folder processing is available through the CLI below.

### Linux application drawer / menu shortcut

Installing with pipx creates a terminal command, but does **not** automatically add
an application-menu shortcut on a new PC. After installing the GUI, run the following
from this repository folder. It creates a shortcut and copies the included icon into
your user account:

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

launcher = shutil.which('humanize-gui')
if not launcher:
    raise SystemExit('humanize-gui is not on PATH. Run pipx ensurepath and reopen the terminal.')
icon_source = Path('assets/mkb-humanizer.svg')
if not icon_source.is_file():
    raise SystemExit('Run this from the repository folder containing assets/.')
icons = Path.home() / '.local/share/icons'
apps = Path.home() / '.local/share/applications'
icons.mkdir(parents=True, exist_ok=True)
apps.mkdir(parents=True, exist_ok=True)
icon = icons / 'mkb-humanizer.svg'
shutil.copyfile(icon_source, icon)
# Desktop Entry Exec uses double quotes and escapes reserved characters.
quoted_launcher = launcher.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
entry = (
    '[Desktop Entry]\nType=Application\nName=MKB Humanizer\n'
    'Comment=Rewrite text and documents with a local Ollama model\n'
    f'Exec="{quoted_launcher}"\nIcon={icon}\n'
    'Terminal=false\nCategories=Office;\nKeywords=humanizer;rewrite;Ollama;\n'
)
(apps / 'mkb-humanizer.desktop').write_text(entry, encoding='utf-8')
print('Shortcut created. Search the application menu for MKB Humanizer.')
PY
```

If available, refresh the menu database:

```bash
update-desktop-database ~/.local/share/applications
```

On GNOME/Ubuntu, press **Super/Windows**, search **MKB Humanizer**, and open it. You
can pin it to Favorites. Other desktops provide an equivalent application menu.

### Windows Start menu shortcut

After installing the GUI, run in PowerShell:

```powershell
$launcher = (Get-Command humanize-gui -ErrorAction Stop).Source
$menu = Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'Microsoft\Windows\Start Menu\Programs'
New-Item -ItemType Directory -Force -Path $menu | Out-Null
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $menu 'MKB Humanizer.lnk'))
$shortcut.TargetPath = $launcher
$shortcut.Description = 'Rewrite text and documents with a local Ollama model'
$shortcut.Save()
```

Search **MKB Humanizer** in Start. This uses the pipx executable; a terminal window
may also appear on Windows. Keep Ollama running in the background.

## 6. Use the command line

Verify the installation:

```text
humanize --version
humanize --help
humanize-batch --help
```

The version currently prints `hz 0.2.0-local`. `hz` is an alias of `humanize`.

### Pasted / piped text

Linux:

```bash
echo 'This solution serves as a testament to our commitment to innovation.' | humanize
```

Windows PowerShell:

```powershell
"This solution serves as a testament to our commitment to innovation." | humanize
```

### Text, Markdown, and Word files

These one-line commands work on both platforms. Quote paths containing spaces:

```text
humanize draft.txt -o draft.human.txt
humanize article.md -o article.human.md
humanize "My Report.docx" -o "My Report.human.docx"
```

Use separate input and output paths. Unlike the GUI, the CLI can replace an existing
output file without a confirmation dialog, so choose output paths carefully.

Select a model explicitly when multiple Humanizer variants are installed:

```text
humanize article.md -o article.human.md --ollama-model hf.co/jialinyyzz/humanizer:Q4_K_M
```

The default server is `http://127.0.0.1:11434`. To use an existing Ollama server at
another address, specify `--ollama-url` (or change the GUI's address field):

```text
humanize article.md -o article.human.md --ollama-url http://SERVER_ADDRESS:11434 --ollama-model hf.co/jialinyyzz/humanizer:Q4_K_M
```

With a remote server, your text is sent to that server. The selected model must be
installed on the server you connect to.

### Folder processing

```text
humanize-batch ./drafts ./humanized --report-dir ./reports
```

The batch command walks folders recursively. Existing outputs are skipped so you
can resume interrupted jobs. Its explicit model option is **`--model`**, whereas
`humanize` uses **`--ollama-model`**:

```text
humanize-batch ./drafts ./humanized --model hf.co/jialinyyzz/humanizer:Q4_K_M --report-dir ./reports
```

### Quality report and preview

```text
humanize article.md -o article.human.md --json --quiet > article.report.json
humanize article.md --dry-run
```

`--json` emits per-piece copy rates, missing/added numbers, missing URLs, retries,
and flagged pieces. `--dry-run` previews how the input will be split without calling
a model. In Windows PowerShell, redirected report-file encoding depends on your
PowerShell version; for a UTF-8 report you can also use the GUI's **Export report**.

## Preservation and language limits

Markdown headings, code blocks, tables, front matter, link-only lines, math blocks,
block quotes, and reference sections are kept. Long prose is split into pieces and
restored in place.

For DOCX, headings, tables, links, images, fields, equations, headers, footers, and
reference sections are left alone. Rewritten paragraphs retain their paragraph style.
Mixed bold or italic formatting inside a rewritten paragraph is lost because it takes
the formatting of its first run.

The author documents Humanizer for **English and Chinese** rewriting. **Hindi and
Hinglish quality are untested**; Unicode input support is not a quality guarantee.
Devanagari display depends on installed fonts. See the
[model card](https://huggingface.co/jialinyyzz/humanizer) for training and evaluation details.

Always review names, dates, numbers, quotations, and meaning. Automated checks cannot
detect every factual change or a claim becoming stronger or weaker. No AI-detector
result is guaranteed.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `humanize` / `humanize-gui` not found | Run `pipx ensurepath`, reopen the terminal, and check `pipx list`. Use `py -m pipx ensurepath` if needed on Windows. |
| GUI asks for PySide6 | From the repo folder, run `pipx install '.[gui]' --force`. |
| DOCX support missing | Install `'.[docx]'` or `'.[gui]'`. For an existing CLI installation, `pipx inject humanize-model python-docx` also works. |
| Cannot inject into nonexistent environment | Install the project first. Cloning alone creates no pipx environment. |
| Ollama unreachable / no models | Run `ollama list`; start Ollama, verify its address, install the model, and refresh the GUI. |
| Explicit model not installed | Copy the exact name/tag from `ollama list`; check that you are querying the intended server. |
| Out of memory or slow generation | Close other large applications, use a smaller Humanizer variant, or review GPU support. Avoid simultaneous large rewrite jobs. |
| GUI does not display on Linux | Run in a graphical desktop session. If Qt names a missing system library, install that dependency through your package manager. For Ubuntu's missing xcb-cursor error, install `libxcb-cursor0`. |

For GPU diagnostics, start a rewrite and run `ollama ps` in another terminal. On an
NVIDIA machine, `nvidia-smi` can also show GPU usage. GPU acceleration is optional;
see Ollama's platform guides for supported hardware and drivers.

### Old pipx: `JSONDecodeError` / missing pip

Inspect the pipx log for the underlying error. If it says `No module named pip`,
the shared environment may be stale after a Python upgrade. Use the shared Python
path from your own log; an example for older Linux pipx installations is:

```bash
~/.local/pipx/shared/bin/python -m ensurepip --upgrade
pipx install '.[gui]' --force
```

If `ensurepip` itself is missing, install your distribution's matching Python venv
package. If a log reports a **symlink loop**, inspect the named link in the command
folder and move the broken link out of that folder before retrying; do not remove
unrelated working applications.

## Update or reinstall

Close the GUI, return to the repository folder, and run:

```text
git pull
pipx install '.[gui]' --force
```

For CLI-only installations, use `'.[docx]'` or `.` instead. Keep the chosen extra in
the reinstall command so the requested dependencies are included. Reopen the app
for code and appearance updates. Your Ollama models are separate from pipx and do
not need downloading again just because you reinstall this toolkit.

## Development checks

Install the GUI dependencies in a development environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install '.[gui]'
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

These integration checks use a local test server, not model inference. They cover
text and document processing, preservation, cancellation, failure handling, and
input/output safety.

## Credits and backend details

This project preserves structured-file handling and quality checks from
[`sgaofen/humanizer-local-model`](https://github.com/sgaofen/humanizer-local-model),
adds Ollama as a native backend and a resumable batch command, and provides the
MKB Humanizer desktop interface.

The specialized backend sends the model's exact raw completion prompt with temperature
1.0, top-p 0.95, top-k 0, min-p 0, repeat penalty 1.0, and no stop string. The optional
`reference-humanizer-local-model/` checkout is for comparison and is not required to
run this toolkit.
