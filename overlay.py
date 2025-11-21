import sys, json, win32api, win32con, win32gui, math
from PyQt6.QtWidgets import (QApplication, QWidget, QColorDialog, QPushButton, QLabel, 
                              QLineEdit, QComboBox, QFileDialog, QVBoxLayout, QHBoxLayout,
                              QStackedWidget, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPolygonF, QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QSize
import qtawesome as qta
import os

def get_icon_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'icon.ico')
    return 'icon.ico'

SETTINGS_FILE = "settings.json"

DARK_BG = "#0f1610"       # very dark soft green (almost black)
CARD_BG = "#142015"       # muted dark green
ACCENT = "#1c4d1f"        # soft natural green (not bright)
HIGHLIGHT = "#3e7a47"     # gentle highlight green, not saturated
TEXT = "#c4cfd1"
TEXT_DIM = "#c4cfd1"

STYLE = f"""
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT};
    font-family: 'Segoe UI', Arial;
}}
QPushButton {{
    background-color: {ACCENT};
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {HIGHLIGHT};
}}
QLineEdit, QComboBox {{
    background-color: {CARD_BG};
    border: 2px solid {ACCENT};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {HIGHLIGHT};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT};
    margin-right: 10px;
}}
QLabel {{
    background: transparent;
}}
"""

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        default = {"num_dots": 10, "follow_speed": 0.25, "lag_speed": 0.20, "max_size": 20, "color": [0, 255, 255], "shape": "Circle", "image_path": ""}
        save_settings(default)
        return default

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)

def draw_shape(painter, shape, pos, size, color, pixmap=None):
    painter.setBrush(QBrush(color))
    size = max(1, int(size))
    x, y = pos.x(), pos.y()

    if shape == "Image" and pixmap and not pixmap.isNull():
        scaled = pixmap.scaled(size * 2, size * 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        painter.setOpacity(color.alphaF())
        painter.drawPixmap(int(x), int(y), scaled)
        painter.setOpacity(1.0)
        return
    if shape == "Circle":
        painter.drawEllipse(QPointF(x + size, y + size), size, size)
    elif shape == "Square":
        painter.drawRect(int(x), int(y), size * 2, size * 2)
    elif shape == "Diamond":
        poly = QPolygonF([QPointF(x + size, y), QPointF(x + size * 2, y + size), QPointF(x + size, y + size * 2), QPointF(x, y + size)])
        painter.drawPolygon(poly)
    elif shape == "Triangle":
        poly = QPolygonF([QPointF(x + size, y), QPointF(x + size * 2, y + size * 2), QPointF(x, y + size * 2)])
        painter.drawPolygon(poly)
    elif shape == "Star":
        poly = QPolygonF()
        cx, cy = x + size, y + size
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = size if i % 2 == 0 else size // 2
            poly.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))
        painter.drawPolygon(poly)
    elif shape == "Hexagon":
        poly = QPolygonF()
        cx, cy = x + size, y + size
        for i in range(6):
            angle = i * math.pi / 3
            poly.append(QPointF(cx + size * math.cos(angle), cy + size * math.sin(angle)))
        painter.drawPolygon(poly)
    elif shape == "Pentagon":
        poly = QPolygonF()
        cx, cy = x + size, y + size
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2
            poly.append(QPointF(cx + size * math.cos(angle), cy + size * math.sin(angle)))
        painter.drawPolygon(poly)
    elif shape == "Heart":
        poly = QPolygonF()
        cx, cy = x + size, y + size
        for i in range(100):
            t = i * 2 * math.pi / 100
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            poly.append(QPointF(cx + hx * size / 17, cy + hy * size / 17))
        painter.drawPolygon(poly)
    elif shape == "Cross":
        w = size // 3
        cx, cy = x + size, y + size
        poly = QPolygonF([QPointF(cx - w, cy - size), QPointF(cx + w, cy - size), QPointF(cx + w, cy - w), QPointF(cx + size, cy - w), QPointF(cx + size, cy + w), QPointF(cx + w, cy + w), QPointF(cx + w, cy + size), QPointF(cx - w, cy + size), QPointF(cx - w, cy + w), QPointF(cx - size, cy + w), QPointF(cx - size, cy - w), QPointF(cx - w, cy - w)])
        painter.drawPolygon(poly)
    elif shape == "Crescent":
        from PyQt6.QtGui import QPainterPath
        cx, cy = x + size, y + size
        path = QPainterPath()
        path.addEllipse(QRectF(cx - size, cy - size, size * 2, size * 2))
        inner = QPainterPath()
        inner.addEllipse(QRectF(cx - size * 0.3, cy - size, size * 1.8, size * 2))
        path = path.subtracted(inner)
        painter.drawPath(path)
    elif shape == "Oval":
        painter.drawEllipse(int(x), int(y), size * 2, size)
    elif shape == "Arrow":
        poly = QPolygonF([QPointF(x + size, y), QPointF(x + size * 2, y + size), QPointF(x + size * 1.5, y + size), QPointF(x + size * 1.5, y + size * 2), QPointF(x + size * 0.5, y + size * 2), QPointF(x + size * 0.5, y + size), QPointF(x, y + size)])
        painter.drawPolygon(poly)
    elif shape == "Mouse":
        poly = QPolygonF([QPointF(x, y), QPointF(x, y + size * 1.6), QPointF(x + size * 0.3, y + size * 1.25), QPointF(x + size * 0.5, y + size * 1.7), QPointF(x + size * 0.75, y + size * 1.55), QPointF(x + size * 0.5, y + size * 1.1), QPointF(x + size * 1.0, y + size * 1.1)])
        painter.drawPolygon(poly)


class Overlay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.pixmap = QPixmap()
        self._load_image()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.dots = [QPointF(screen.width() // 2, screen.height() // 2) for _ in range(self.settings["num_dots"])]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(16)
        self.show()
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    def _load_image(self):
        path = self.settings.get("image_path", "")
        self.pixmap = QPixmap(path) if path else QPixmap()

    def update_overlay(self):
        mouse_x, mouse_y = win32api.GetCursorPos()
        s = load_settings()
        if s.get("image_path", "") != self.settings.get("image_path", ""):
            self.settings = s
            self._load_image()
        else:
            self.settings = s
        if len(self.dots) != s["num_dots"]:
            screen = QApplication.primaryScreen().geometry()
            self.dots = [QPointF(screen.width() // 2, screen.height() // 2) for _ in range(s["num_dots"])]
        if len(self.dots) < 1:
            return
        lead = self.dots[0]
        lead.setX(lead.x() + (mouse_x - lead.x()) * s["follow_speed"])
        lead.setY(lead.y() + (mouse_y - lead.y()) * s["follow_speed"])
        for i in range(1, len(self.dots)):
            prev, curr = self.dots[i - 1], self.dots[i]
            curr.setX(curr.x() + (prev.x() - curr.x()) * s["lag_speed"])
            curr.setY(curr.y() + (prev.y() - curr.y()) * s["lag_speed"])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        r, g, b = self.settings["color"]
        shape, max_size, n = self.settings["shape"], self.settings["max_size"], len(self.dots)
        for i, dot in enumerate(self.dots):
            alpha = max(10, int(255 * (1 - i / max(n, 1))))
            size = max(1, max_size - (i * (max_size / max(n, 1))))
            draw_shape(painter, shape, dot, size, QColor(r, g, b, alpha), self.pixmap)


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Mouse Follower")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {HIGHLIGHT};")
        layout.addWidget(title)
        
        subtitle = QLabel("Customize your cursor trail effect")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        self.status_card = QFrame()
        self.status_card.setFixedSize(280, 200)
        self.status_card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 20px;")
        card_layout = QVBoxLayout(self.status_card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(15)
        
        self.status_icon = QLabel()
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_icon.setPixmap(qta.icon('mdi6.cursor-default-outline', color=TEXT_DIM).pixmap(QSize(64, 64)))
        card_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Stopped")
        self.status_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)
        
        card_container = QHBoxLayout()
        card_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_container.addWidget(self.status_card)
        layout.addLayout(card_container)
        
        layout.addSpacing(30)
        
        self.toggle_btn = QPushButton("  Start")
        self.toggle_btn.setIcon(qta.icon('mdi6.play', color=TEXT))
        self.toggle_btn.setIconSize(QSize(24, 24))
        self.toggle_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.toggle_btn.setFixedSize(200, 60)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT};
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: #3d5c3d;
            }}
        """)
        self.toggle_btn.clicked.connect(self.toggle_overlay)
        
        btn_container = QHBoxLayout()
        btn_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_container.addWidget(self.toggle_btn)
        layout.addLayout(btn_container)
        
        layout.addStretch()
        self.is_running = False

    def toggle_overlay(self):
        if self.is_running:
            if self.overlay:
                self.overlay.timer.stop()
                self.overlay.close()
                self.overlay = None
            self.is_running = False
            self.toggle_btn.setText("  Start")
            self.toggle_btn.setIcon(qta.icon('mdi6.play', color=TEXT))
            self.toggle_btn.setStyleSheet(f"QPushButton {{background-color: {HIGHLIGHT}; border-radius: 16px;}} QPushButton:hover {{background-color: #3d5c3d;}}")
            self.status_label.setText("Stopped")
            self.status_icon.setPixmap(qta.icon('mdi6.cursor-default-outline', color=TEXT_DIM).pixmap(QSize(64, 64)))
        else:
            self.overlay = Overlay(load_settings())
            self.is_running = True
            self.toggle_btn.setText("  Stop")
            self.toggle_btn.setIcon(qta.icon('mdi6.stop', color=TEXT))
            self.toggle_btn.setStyleSheet(f"QPushButton {{background-color: {ACCENT}; border-radius: 16px;}} QPushButton:hover {{background-color: #3d5c3d;}}")
            self.status_label.setText("Running")
            self.status_icon.setPixmap(qta.icon('mdi6.cursor-default', color='#2ecc71').pixmap(QSize(64, 64)))


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.s = load_settings()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)
        
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {HIGHLIGHT};")
        layout.addWidget(title)
        layout.addSpacing(10)
        
        fields = [("Dots", "num_dots"), ("Follow Speed", "follow_speed"), ("Lag Speed", "lag_speed"), ("Max Size", "max_size")]
        self.inputs = {}
        for label, key in fields:
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 12))
            lbl.setFixedWidth(120)
            inp = QLineEdit(str(self.s[key]))
            inp.setFixedSize(180, 40)
            self.inputs[key] = inp
            row.addWidget(lbl)
            row.addWidget(inp)
            layout.addLayout(row)
        
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Shape")
        lbl.setFont(QFont("Segoe UI", 12))
        lbl.setFixedWidth(120)
        self.shape_dropdown = QComboBox()
        self.shape_dropdown.setFixedSize(180, 40)
        shapes = ["Circle", "Square", "Diamond", "Triangle", "Star", "Hexagon", "Pentagon", "Heart", "Cross", "Crescent", "Oval", "Arrow", "Mouse", "Image"]
        self.shape_dropdown.addItems(shapes)
        self.shape_dropdown.setCurrentText(self.s["shape"])
        row.addWidget(lbl)
        row.addWidget(self.shape_dropdown)
        layout.addLayout(row)
        
        # Color picker row with preview
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Color")
        lbl.setFont(QFont("Segoe UI", 12))
        lbl.setFixedWidth(120)
        
        color_container = QHBoxLayout()
        color_container.setSpacing(10)
        
        # Color preview box
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(40, 40)
        r, g, b = self.s["color"]
        self.color_preview.setStyleSheet(f"background-color: rgb({r},{g},{b}); border-radius: 8px; border: 2px solid {ACCENT};")
        
        self.color_btn = QPushButton("  Pick Color   ")
        self.color_btn.setIcon(qta.icon('mdi6.palette', color=TEXT))
        self.color_btn.setFixedSize(130, 40)
        self.color_btn.clicked.connect(self.pick_color)
        
        color_container.addWidget(self.color_preview)
        color_container.addWidget(self.color_btn)
        
        row.addWidget(lbl)
        row.addLayout(color_container)
        layout.addLayout(row)
        
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Image")
        lbl.setFont(QFont("Segoe UI", 12))
        lbl.setFixedWidth(120)
        img_btn = QPushButton("  Choose Image")
        img_btn.setIcon(qta.icon('mdi6.image', color=TEXT))
        img_btn.setFixedSize(180, 40)
        img_btn.clicked.connect(self.pick_image)
        row.addWidget(lbl)
        row.addWidget(img_btn)
        layout.addLayout(row)
        
        self.image_label = QLabel(self.s.get("image_path", "") or "No image selected")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        layout.addWidget(self.image_label)
        
        layout.addSpacing(15)
        
        save_btn = QPushButton("  Save Settings")
        save_btn.setIcon(qta.icon('mdi6.content-save', color=TEXT))
        save_btn.setIconSize(QSize(20, 20))
        save_btn.setFixedSize(200, 50)
        save_btn.setStyleSheet(f"QPushButton {{background-color: {HIGHLIGHT}; border-radius: 12px;}} QPushButton:hover {{background-color: #3d5c3d;}}")
        save_btn.clicked.connect(self.save_all)
        
        btn_container = QHBoxLayout()
        btn_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_container.addWidget(save_btn)
        layout.addLayout(btn_container)
        
        layout.addStretch()

    def pick_color(self):
        # Get current color
        r, g, b = self.s["color"]
        current = QColor(r, g, b)
        
        # Open color dialog with current color
        color = QColorDialog.getColor(current, self, "Choose Trail Color")
        
        if color.isValid():
            self.s["color"] = [color.red(), color.green(), color.blue()]
            # Update preview
            self.color_preview.setStyleSheet(f"background-color: rgb({color.red()},{color.green()},{color.blue()}); border-radius: 8px; border: 2px solid {ACCENT};")
            # Save immediately so overlay updates in real-time
            save_settings(self.s)

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
        if path:
            self.s["image_path"] = path
            self.image_label.setText(path)
            save_settings(self.s)

    def save_all(self):
        self.s["num_dots"] = int(self.inputs["num_dots"].text())
        self.s["follow_speed"] = float(self.inputs["follow_speed"].text())
        self.s["lag_speed"] = float(self.inputs["lag_speed"].text())
        self.s["max_size"] = float(self.inputs["max_size"].text())
        self.s["shape"] = self.shape_dropdown.currentText()
        save_settings(self.s)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse Follower")
        self.setWindowIcon(QIcon(get_icon_path()))
        self.resize(450, 700)
        self.setStyleSheet(STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        nav = QFrame()
        nav.setFixedHeight(60)
        nav.setStyleSheet(f"background-color: {CARD_BG};")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.setSpacing(40)
        
        self.home_btn = QPushButton("  Home")
        self.home_btn.setIcon(qta.icon('mdi6.home', color=HIGHLIGHT))
        self.home_btn.setIconSize(QSize(22, 22))
        self.home_btn.setStyleSheet(f"background: transparent; color: {HIGHLIGHT}; font-size: 15px; font-weight: bold;")
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        
        self.settings_btn = QPushButton("  Settings")
        self.settings_btn.setIcon(qta.icon('mdi6.cog', color=TEXT_DIM))
        self.settings_btn.setIconSize(QSize(22, 22))
        self.settings_btn.setStyleSheet(f"background: transparent; color: {TEXT_DIM}; font-size: 15px; font-weight: bold;")
        self.settings_btn.clicked.connect(lambda: self.switch_page(1))
        
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.settings_btn)
        
        layout.addWidget(nav)
        
        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)
        layout.addWidget(self.stack)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.home_btn.setIcon(qta.icon('mdi6.home', color=HIGHLIGHT))
            self.home_btn.setStyleSheet(f"background: transparent; color: {HIGHLIGHT}; font-size: 15px; font-weight: bold;")
            self.settings_btn.setIcon(qta.icon('mdi6.cog', color=TEXT_DIM))
            self.settings_btn.setStyleSheet(f"background: transparent; color: {TEXT_DIM}; font-size: 15px; font-weight: bold;")
        else:
            self.home_btn.setIcon(qta.icon('mdi6.home', color=TEXT_DIM))
            self.home_btn.setStyleSheet(f"background: transparent; color: {TEXT_DIM}; font-size: 15px; font-weight: bold;")
            self.settings_btn.setIcon(qta.icon('mdi6.cog', color=HIGHLIGHT))
            self.settings_btn.setStyleSheet(f"background: transparent; color: {HIGHLIGHT}; font-size: 15px; font-weight: bold;")


app = QApplication(sys.argv)
app.setWindowIcon(QIcon(get_icon_path()))
window = MainWindow()
window.show()
sys.exit(app.exec())