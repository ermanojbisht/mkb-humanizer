"""Desktop front end. Run with humanize-gui or python -m humanizer.gui."""
from __future__ import annotations

import codecs
import json
import os
from pathlib import Path
import sys
import tempfile
import time


def main():
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print('Desktop support is missing. Run: pipx inject humanize-model "PySide6>=6.6,<7"', file=sys.stderr)
        return 1
    app = QApplication(sys.argv)
    app.setApplicationName('MKB Humanizer')
    app.setOrganizationName('LocalHumanizer')
    window = Window()
    window.show()
    return app.exec()


try:
    from PySide6.QtCore import QProcess, QSettings, QTimer, Qt, QSize
    from PySide6.QtWidgets import (
        QApplication, QComboBox, QFileDialog, QFormLayout, QHBoxLayout,
        QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit,
        QProgressBar, QPushButton, QSplitter, QTabWidget, QVBoxLayout, QWidget,
    )
except ImportError:
    pass
else:
    from .gui_style import GlassBackground, STYLE, icon

    class Window(QMainWindow):
        def __init__(self, settings=None):
            super().__init__()
            self.setWindowTitle('MKB Humanizer')
            self.resize(1200, 900)
            self.setMinimumSize(1020, 760)
            self.setStyleSheet(STYLE)
            self.setWindowIcon(icon('sparkles', '#426ee8', 48))
            self.settings = settings if settings is not None else QSettings('LocalHumanizer', 'Local Humanizer')
            self.process = None
            self.discovery = None
            self.temp = None
            self.report = None
            self.cancelled = False
            self.stdout = bytearray()
            self.job_output = None
            self.job_input = None
            self.saved_file = None
            self.started = 0
            root = GlassBackground()
            self.setCentralWidget(root)
            layout = QVBoxLayout(root)
            layout.setContentsMargins(28, 24, 28, 20)
            layout.setSpacing(13)
            header = QHBoxLayout()
            brand = QLabel()
            brand.setObjectName('brand')
            brand.setFixedSize(54, 54)
            brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
            brand.setPixmap(icon('sparkles', '#ffffff', 30).pixmap(30, 30))
            header.addWidget(brand)
            heading = QVBoxLayout()
            heading.setSpacing(3)
            title = QLabel('MKB Humanizer')
            title.setObjectName('title')
            subtitle = QLabel('A clearer voice. The same meaning. ✨')
            subtitle.setObjectName('subtitle')
            heading.addWidget(title)
            heading.addWidget(subtitle)
            header.addLayout(heading)
            header.addStretch()
            badge = QLabel('●  LOCAL FIRST')
            badge.setObjectName('badge')
            badge.setToolTip('Rewriting uses the Ollama server at the address below. Default: your computer.')
            header.addWidget(badge)
            layout.addLayout(header)
            connection_card = QWidget()
            connection_card.setObjectName('connection')
            card_layout = QVBoxLayout(connection_card)
            card_layout.setContentsMargins(16, 13, 16, 12)
            card_layout.setSpacing(8)
            eyebrow = QLabel('MODEL CONNECTION')
            eyebrow.setObjectName('eyebrow')
            card_layout.addWidget(eyebrow)
            connection = QHBoxLayout()
            connection.setSpacing(10)
            self.url = QLineEdit(self.settings.value('url', os.environ.get('OLLAMA_HOST', 'http://127.0.0.1:11434')))
            self.url.setPlaceholderText('Ollama address')
            self.url.setMinimumWidth(240)
            self.url.setCursorPosition(0)
            self.model = QComboBox()
            self.model.setMinimumWidth(360)
            self.refresh = QPushButton('Refresh')
            self.refresh.setIcon(icon('refresh'))
            self.refresh.setToolTip('Discover installed Humanizer models')
            self.refresh.clicked.connect(self.refresh_models)
            connection.addWidget(QLabel('Ollama'))
            connection.addWidget(self.url)
            connection.addWidget(self.model, 2)
            connection.addWidget(self.refresh)
            card_layout.addLayout(connection)
            self.connection_status = QLabel('Connecting to Ollama…')
            self.connection_status.setWordWrap(True)
            self.connection_status.setObjectName('connectionStatus')
            card_layout.addWidget(self.connection_status)
            layout.addWidget(connection_card)
            self.tabs = QTabWidget()
            self.tabs.setIconSize(QSize(18, 18))
            layout.addWidget(self.tabs, 1)
            text_tab = QWidget()
            text_layout = QVBoxLayout(text_tab)
            text_layout.setContentsMargins(12, 16, 12, 12)
            splitter = QSplitter(Qt.Orientation.Horizontal)
            self.original = QPlainTextEdit()
            self.original.setPlaceholderText('Paste your text or Markdown here…')
            self.result = QPlainTextEdit()
            self.result.setReadOnly(True)
            self.result.setPlaceholderText('The rewritten text will appear here.')
            for label, hint, editor in [('Original draft', 'Paste text or Markdown to begin', self.original), ('Refined result', 'Your rewrite, ready for review', self.result)]:
                panel = QWidget()
                column = QVBoxLayout(panel)
                panel_title = QLabel(label)
                panel_title.setObjectName('panelTitle')
                column.addWidget(panel_title)
                caption = QLabel(hint)
                caption.setObjectName('muted')
                column.addWidget(caption)
                column.addWidget(editor)
                splitter.addWidget(panel)
            text_layout.addWidget(splitter)
            actions = QHBoxLayout()
            self.copy = QPushButton('Copy')
            self.copy.setIcon(icon('copy'))
            self.save = QPushButton('Save text…')
            self.save.setIcon(icon('save'))
            self.copy.clicked.connect(lambda: QApplication.clipboard().setText(self.result.toPlainText()))
            self.save.clicked.connect(self.save_text)
            self.copy.setEnabled(False)
            self.save.setEnabled(False)
            actions.addStretch()
            actions.addWidget(self.copy)
            actions.addWidget(self.save)
            text_layout.addLayout(actions)
            self.tabs.addTab(text_tab, icon('text'), 'Text studio')
            file_tab = QWidget()
            file_layout = QVBoxLayout(file_tab)
            file_layout.setContentsMargins(24, 24, 24, 24)
            file_layout.setSpacing(18)
            document_title = QLabel('Refine a document')
            document_title.setObjectName('panelTitle')
            file_layout.addWidget(document_title)
            file_layout.addWidget(QLabel('Choose your original and where to save the rewritten version.'))
            form = QFormLayout()
            self.input_path = QLineEdit()
            self.output_path = QLineEdit()
            for label, field, callback in [('Input file', self.input_path, self.pick_input), ('Output file', self.output_path, self.pick_output)]:
                row = QHBoxLayout()
                row.addWidget(field)
                button = QPushButton('Browse…')
                button.setIcon(icon('folder'))
                button.clicked.connect(callback)
                row.addWidget(button)
                form.addRow(label, row)
            file_layout.addLayout(form)
            note = QLabel('Supported: .txt, .md, .docx. The original is preserved.\nDOCX layout is retained; rewritten paragraphs may lose mixed bold/italic formatting.')
            note.setWordWrap(True)
            file_layout.addWidget(note)
            self.file_status = QLabel('Choose a document and a separate output file.')
            self.file_status.setWordWrap(True)
            file_layout.addWidget(self.file_status)
            file_layout.addStretch()
            self.tabs.addTab(file_tab, icon('file'), 'Documents')
            run_row = QHBoxLayout()
            self.rewrite = QPushButton('Humanize')
            self.rewrite.setObjectName('primary')
            self.rewrite.setIcon(icon('sparkles', '#ffffff'))
            self.rewrite.clicked.connect(self.start_rewrite)
            self.cancel = QPushButton('Cancel')
            self.cancel.setIcon(icon('stop'))
            self.cancel.setEnabled(False)
            self.cancel.clicked.connect(self.cancel_job)
            self.progress = QProgressBar()
            self.progress.setTextVisible(False)
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            run_row.addWidget(self.rewrite)
            run_row.addWidget(self.cancel)
            run_row.addWidget(self.progress, 1)
            layout.addLayout(run_row)
            self.status = QLabel('Ready when you are')
            self.status.setObjectName('muted')
            layout.addWidget(self.status)
            activity_row = QHBoxLayout()
            activity_title = QLabel('ACTIVITY & QUALITY CHECKS')
            activity_title.setObjectName('eyebrow')
            activity_row.addWidget(activity_title)
            activity_row.addStretch()
            self.export = QPushButton('Export report')
            self.export.setIcon(icon('file'))
            self.export.setEnabled(False)
            self.export.clicked.connect(self.save_report)
            activity_row.addWidget(self.export)
            layout.addLayout(activity_row)
            self.log = QPlainTextEdit()
            self.log.setObjectName('activity')
            self.log.setReadOnly(True)
            self.log.setFixedHeight(105)
            self.log.setPlaceholderText('Progress and quality warnings appear here.')
            layout.addWidget(self.log)
            footer_row = QHBoxLayout()
            shield = QLabel()
            shield.setPixmap(icon('shield', '#5275ae', 18).pixmap(18, 18))
            footer_row.addWidget(shield)
            footer = QLabel('Review names, dates, numbers and meaning. Hindi quality is untested.')
            footer.setObjectName('muted')
            footer.setWordWrap(True)
            footer_row.addWidget(footer, 1)
            layout.addLayout(footer_row)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_elapsed)
            QTimer.singleShot(0, self.refresh_models)

        def message(self, text):
            QMessageBox.warning(self, 'MKB Humanizer', text)

        def refresh_models(self):
            if self.discovery or self.process:
                return
            self.refresh.setEnabled(False)
            self.rewrite.setEnabled(False)
            self.connection_status.setText('Connecting to Ollama…')
            self.discovery = QProcess(self)
            proc = self.discovery
            self.model_data = bytearray()
            proc.readyReadStandardOutput.connect(lambda: self.model_data.extend(bytes(proc.readAllStandardOutput())))
            proc.finished.connect(self.models_finished)
            proc.errorOccurred.connect(lambda error: self.models_failed(proc.errorString()) if error == QProcess.ProcessError.FailedToStart else None)
            script = 'import json,sys; from humanizer.hz import ollama_models,_norm_url; print(json.dumps(ollama_models(_norm_url(sys.argv[1]))))'
            proc.start(sys.executable, ['-c', script, self.url.text().strip()])

        def models_failed(self, reason):
            self.connection_status.setText('Could not load models: ' + reason)
            self.model.clear()
            self.refresh.setEnabled(True)
            self.rewrite.setEnabled(False)
            if self.discovery:
                self.discovery.deleteLater()
            self.discovery = None

        def models_finished(self, code, _status):
            try:
                names = json.loads(bytes(self.model_data)) if code == 0 else None
                if names is None:
                    raise ValueError('Ollama is unreachable. Start Ollama and check its address.')
                names = sorted(n for n in names if 'humanizer' in n.lower())
                if not names:
                    raise ValueError('No Humanizer model found. Install one with Ollama, then refresh.')
            except (ValueError, TypeError) as error:
                self.models_failed(str(error))
                return
            selected = self.model.currentText() or self.settings.value('model', '')
            self.model.clear()
            self.model.addItems(names)
            if selected in names:
                self.model.setCurrentText(selected)
            self.connection_status.setText('●  Connected · Humanizer model ready')
            self.settings.setValue('url', self.url.text().strip())
            self.discovery.deleteLater()
            self.discovery = None
            self.refresh.setEnabled(True)
            self.rewrite.setEnabled(True)

        def pick_input(self):
            path, _ = QFileDialog.getOpenFileName(self, 'Choose document', '', 'Documents (*.txt *.md *.docx)')
            if path:
                self.input_path.setText(path)
                source = Path(path)
                self.output_path.setText(str(source.with_name(source.stem + '.human' + source.suffix)))

        def pick_output(self):
            path, _ = QFileDialog.getSaveFileName(self, 'Save rewritten document', self.output_path.text(), 'Documents (*.txt *.md *.docx)')
            if path:
                self.output_path.setText(path)

        def confirm_destination(self, target, source=None):
            if source and (target.resolve() == source.resolve() or (target.exists() and os.path.samefile(target, source))):
                raise ValueError('Choose an output different from the original file.')
            if not target.parent.is_dir():
                raise ValueError('The output folder does not exist.')
            if target.is_dir():
                raise ValueError('Choose a file, not a folder.')
            if target.exists():
                return QMessageBox.question(self, 'Replace existing output?', f'Replace {target}?') == QMessageBox.StandardButton.Yes
            return True

        def start_rewrite(self):
            if self.process or self.discovery:
                return
            if not self.model.currentText():
                self.message('Connect to Ollama and select a Humanizer model first.')
                return
            self.job_output = None
            self.job_input = None
            try:
                if self.tabs.currentIndex() == 1:
                    source = Path(self.input_path.text().strip()).expanduser()
                    target = Path(self.output_path.text().strip()).expanduser()
                    if not source.is_file() or source.suffix.lower() not in ('.txt', '.md', '.docx'):
                        raise ValueError('Choose an existing .txt, .md or .docx input.')
                    if not self.output_path.text().strip():
                        raise ValueError('Choose an output file.')
                    if target.suffix.lower() != source.suffix.lower():
                        raise ValueError('Use the same file extension for input and output.')
                    if not self.confirm_destination(target, source):
                        return
                    self.job_input, self.job_output = source, target
                    # Keep partial output separate; publish only after a successful rewrite.
                    self.temp = tempfile.TemporaryDirectory(prefix='.humanizer-', dir=str(target.parent))
                    self.staged_output = Path(self.temp.name) / ('result' + target.suffix)
                    args = [str(source), '-o', str(self.staged_output)]
                else:
                    if not self.original.toPlainText().strip():
                        raise ValueError('Paste some text first.')
                    self.temp = tempfile.TemporaryDirectory(prefix='humanizer-')
                    source = Path(self.temp.name) / 'draft.md'
                    source.write_text(self.original.toPlainText(), encoding='utf-8')
                    args = [str(source)]
            except (OSError, ValueError) as error:
                self.message(str(error))
                self.cleanup()
                return
            self.report = None
            self.export.setEnabled(False)
            self.saved_file = None
            if self.job_output:
                self.file_status.setText('Rewriting document…')
            self.log.clear()
            self.stdout = bytearray()
            self.decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
            self.cancelled = False
            self.started = time.monotonic()
            self.settings.setValue('model', self.model.currentText())
            self.set_busy(True)
            self.process = QProcess(self)
            proc = self.process
            proc.readyReadStandardOutput.connect(lambda: self.stdout.extend(bytes(proc.readAllStandardOutput())))
            proc.readyReadStandardError.connect(self.read_progress)
            proc.finished.connect(self.rewrite_finished)
            proc.errorOccurred.connect(lambda error: self.start_failed(proc.errorString()) if error == QProcess.ProcessError.FailedToStart else None)
            proc.start(sys.executable, ['-m', 'humanizer.hz', *args, '--json', '--no-launch', '--ollama-url', self.url.text().strip(), '--ollama-model', self.model.currentText()])

        def read_progress(self):
            text = self.decoder.decode(bytes(self.process.readAllStandardError()))
            if text:
                cursor = self.log.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.insertText(text)
                self.log.setTextCursor(cursor)
                self.log.ensureCursorVisible()

        def set_busy(self, busy):
            for widget in (self.tabs, self.model, self.url, self.refresh):
                widget.setEnabled(not busy)
            self.rewrite.setEnabled(not busy and self.model.count() > 0)
            self.cancel.setEnabled(busy)
            self.progress.setRange(0, 0 if busy else 1)
            self.progress.setValue(0)
            if busy:
                self.timer.start(1000)
                self.update_elapsed()
            else:
                self.timer.stop()

        def update_elapsed(self):
            self.status.setText(f'Rewriting… {int(time.monotonic() - self.started)} seconds • first use may need time to load the model')

        def cancel_job(self):
            if self.process:
                self.cancelled = True
                self.process.kill()
                self.cancel.setEnabled(False)

        def start_failed(self, reason):
            self.status.setText('Could not start rewrite')
            self.message(reason)
            self.finish_job()

        def rewrite_finished(self, code, _status):
            self.read_progress()
            self.stdout.extend(bytes(self.process.readAllStandardOutput()))
            try:
                if self.cancelled:
                    self.status.setText('Cancelled. No new output was saved.')
                    if self.job_output:
                        self.file_status.setText('Cancelled. No new output was saved.')
                    return
                if code != 0:
                    raise ValueError('Rewrite failed. See the progress area for details.')
                report = json.loads(bytes(self.stdout))
                if self.job_output:
                    # Recheck input aliases in case a path changed during generation.
                    if self.job_output.resolve() == self.job_input.resolve() or (self.job_output.exists() and os.path.samefile(self.job_output, self.job_input)):
                        raise ValueError('Output now points to the original. Result was not saved.')
                    os.replace(self.staged_output, self.job_output)
                    report['input'] = str(self.job_input)
                    report['output'] = str(self.job_output)
                    self.saved_file = self.job_output
                    self.file_status.setText(f'Saved: {self.job_output}')
                else:
                    report['input'] = 'pasted text'
                    self.result.setPlainText(report.get('text', ''))
                    self.copy.setEnabled(bool(self.result.toPlainText()))
                    self.save.setEnabled(bool(self.result.toPlainText()))
                self.report = report
                self.export.setEnabled(True)
                summary = report['summary']
                self.status.setText(f"Done • {summary['pieces']} pieces • {summary['seconds']} seconds • {summary['flagged']} flagged for review")
                self.progress.setRange(0, 1)
                self.progress.setValue(1)
            except (ValueError, KeyError, OSError) as error:
                self.status.setText('Rewrite could not be completed')
                if self.job_output:
                    self.file_status.setText('Rewrite failed. No new output was saved.')
                self.message(str(error))
            finally:
                self.finish_job()

        def cleanup(self):
            if self.temp:
                self.temp.cleanup()
                self.temp = None

        def finish_job(self):
            if self.process:
                self.process.deleteLater()
                self.process = None
            self.set_busy(False)
            if self.report is not None:
                self.progress.setValue(1)
            self.cleanup()

        def save_text(self):
            path, _ = QFileDialog.getSaveFileName(self, 'Save rewritten text', 'rewrite.md', 'Markdown (*.md);;Text (*.txt)')
            if path:
                try:
                    Path(path).write_text(self.result.toPlainText(), encoding='utf-8')
                except OSError as error:
                    self.message(str(error))

        def save_report(self):
            path, _ = QFileDialog.getSaveFileName(self, 'Save quality report', 'rewrite.report.json', 'JSON (*.json)')
            if path and self.report:
                try:
                    target = Path(path)
                    if self.job_input and (target.resolve() == self.job_input.resolve() or (target.exists() and os.path.samefile(target, self.job_input))):
                        raise ValueError('The report cannot overwrite the original document.')
                    if self.saved_file and target.resolve() == self.saved_file.resolve():
                        raise ValueError('The report cannot overwrite the rewritten document.')
                    target.write_text(json.dumps(self.report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                except (OSError, ValueError) as error:
                    self.message(str(error))

        def closeEvent(self, event):
            if self.process:
                answer = QMessageBox.question(self, 'Rewrite in progress', 'Cancel this rewrite and close?')
                if answer != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return
                self.cancelled = True
                self.process.kill()
                self.process.waitForFinished(3000)
            if self.discovery:
                self.discovery.kill()
                self.discovery.waitForFinished(3000)
            self.cleanup()
            event.accept()


if __name__ == '__main__':
    sys.exit(main())
