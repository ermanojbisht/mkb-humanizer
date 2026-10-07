"""Shared desktop colors and small, scalable line icons."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    'sparkles': '<path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3Z"/><path d="m20 2 .7 2.3L23 5l-2.3.7L20 8l-.7-2.3L17 5l2.3-.7Z"/>',
    'refresh': '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6.1 6.1A8 8 0 0 1 20 12M4 12a8 8 0 0 0 13.9 5.9"/>',
    'copy': '<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    'save': '<path d="M12 3v12m-5-5 5 5 5-5M4 16v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4"/>',
    'file': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6M8 13h8M8 17h6"/>',
    'text': '<path d="M4 5h16M12 5v15M8 20h8M4 5v3M20 5v3"/>',
    'folder': '<path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v1M3 9h18l-3 11H3Z"/>',
    'stop': '<rect x="5" y="5" width="14" height="14" rx="3"/>',
    'shield': '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
}


def icon(name, color='#526f9e', size=24):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{PATHS[name]}</svg>'
    # Render at twice logical resolution for sharp icons on HiDPI displays.
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)


class GlassBackground(QWidget):
    """Soft gradient light behind translucent cards, painted at any window size."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        base = QLinearGradient(0, 0, self.width(), self.height())
        base.setColorAt(0, QColor('#e6efff'))
        base.setColorAt(.5, QColor('#edf1ff'))
        base.setColorAt(1, QColor('#dceeff'))
        painter.fillRect(self.rect(), base)
        for x, y, radius, color in [(.05, .12, .55, '#93bcff'), (.91, .3, .5, '#b7aaff'), (.78, .98, .6, '#91d5ff')]:
            glow = QRadialGradient(self.width() * x, self.height() * y, self.width() * radius)
            glow.setColorAt(0, QColor(color))
            clear = QColor(color)
            clear.setAlpha(0)
            glow.setColorAt(1, clear)
            painter.fillRect(self.rect(), glow)
        painter.end()


STYLE = '''
QMainWindow, QMessageBox { background: #eaf0ff; }
QWidget { color: #263c61; font-family: "Noto Sans", "DejaVu Sans", sans-serif; font-size: 13px; }
QLabel { background: transparent; }
QLabel#title { font-size: 27px; font-weight: 700; color: #152e57; }
QLabel#subtitle, QLabel#muted { color: #536b8e; }
QLabel#eyebrow { color: #345ebe; font-size: 11px; font-weight: 700; }
QLabel#brand { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #318dff, stop:.55 #4267e8, stop:1 #7754da); color: white; border: 1px solid rgba(255,255,255,180); border-radius: 16px; }
QLabel#badge { background: rgba(255,255,255,125); color: #315ea9; border: 1px solid rgba(255,255,255,220); border-radius: 14px; padding: 6px 12px; font-size: 11px; font-weight: 600; }
QWidget#connection { background: rgba(255,255,255,145); border: 1px solid rgba(255,255,255,230); border-radius: 16px; }
QLabel#connectionStatus { color: #365fac; padding: 2px 0; font-size: 12px; }
QLabel#panelTitle { font-size: 14px; font-weight: 600; color: #2d4874; }
QLineEdit, QComboBox { background: rgba(255,255,255,165); border: 1px solid #c2d3f0; border-radius: 9px; padding: 9px 10px; selection-background-color: #c1d9ff; min-height: 18px; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #4c83ef; background: rgba(255,255,255,225); }
QComboBox { padding-right: 26px; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background: #f7faff; selection-background-color: #dce9ff; selection-color: #224f9d; border: 1px solid #c2d3f0; padding: 6px; }
QPlainTextEdit { background: rgba(255,255,255,155); border: 1px solid rgba(180,202,237,190); border-radius: 12px; padding: 13px; selection-background-color: #c1d9ff; font-size: 14px; }
QPlainTextEdit:focus { border: 1px solid #4c83ef; background: rgba(255,255,255,195); }
QPlainTextEdit#activity { background: rgba(239,246,255,150); border: 1px solid rgba(255,255,255,220); color: #516b90; font-size: 12px; padding: 9px; }
QPushButton { background: rgba(255,255,255,160); border: 1px solid rgba(255,255,255,230); border-radius: 10px; padding: 9px 14px; font-weight: 600; min-height: 18px; }
QPushButton:hover { background: rgba(255,255,255,235); border-color: #9abaf1; }
QPushButton:pressed { background: #d9e7ff; }
QPushButton:disabled { color: #7b8ca8; background: rgba(239,245,255,125); border-color: rgba(255,255,255,170); }
QPushButton#primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2587f3, stop:.55 #3e68e8, stop:1 #7056d9); border: 1px solid #5485eb; color: white; padding: 11px 24px; }
QPushButton#primary:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1677df, stop:1 #6546cd); }
QPushButton#primary:pressed { background: #315bc7; }
QPushButton#primary:disabled { background: #a4b9e3; border-color: #bacced; color: #f5f8ff; }
QTabWidget::pane { background: rgba(255,255,255,125); border: 1px solid rgba(255,255,255,235); border-radius: 16px; top: -1px; }
QTabBar::tab { background: transparent; color: #526c93; padding: 12px 20px; margin-right: 6px; border-bottom: 3px solid transparent; font-weight: 600; }
QTabBar::tab:selected { color: #275bcc; border-bottom: 3px solid #477eef; }
QTabBar::tab:hover { color: #275bcc; background: rgba(255,255,255,100); }
QProgressBar { border: none; background: rgba(123,155,212,45); border-radius: 4px; min-height: 8px; max-height: 8px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2b92fa, stop:1 #7962e6); border-radius: 4px; }
QSplitter::handle { background: transparent; width: 10px; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 4px; }
QScrollBar::handle:vertical { background: #a9bee2; border-radius: 3px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QToolTip { background: #244778; color: white; border: none; padding: 7px; }
'''
