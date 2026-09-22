import os
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QMovie, QPixmap, QIcon
from PyQt6.QtWidgets import QLabel, QWidget, QMenu, QSystemTrayIcon, QApplication
from config import Config

SIZES = {"小": 80, "中": 120, "大": 160}


class PetWidget(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self._panel = None
        self._drag_pos = QPoint()
        self._press_pos = QPoint()
        self._size = config.get("pet_size") or 120
        self._setup_window()
        self._setup_tray()
        self._load_skin(config.get("current_skin"))

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self._size, self._size)
        x = self._config.get("window_x") or 100
        y = self._config.get("window_y") or 100
        self.move(x, y)

        self._label = QLabel(self)
        self._label.resize(self._size, self._size)

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        skin_path = self._config.get("current_skin") or ""
        if skin_path and os.path.exists(skin_path):
            self._tray.setIcon(QIcon(skin_path))
        else:
            self._tray.setIcon(QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_ComputerIcon))
        self._tray.setToolTip("桌宠")
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示桌宠")
        show_action.triggered.connect(self._show_pet)
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)
        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_pet()

    def _hide_all(self):
        if self._panel:
            self._panel.hide()
        self.hide()

    def _show_pet(self):
        self.show()
        self.raise_()

    def _load_skin(self, path: str):
        if path and os.path.exists(path):
            if path.lower().endswith(".gif"):
                self._movie = QMovie(path)
                self._movie.setScaledSize(QSize(self._size, self._size))
                self._label.setMovie(self._movie)
                self._movie.start()
            else:
                pixmap = QPixmap(path).scaled(
                    self._size, self._size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._label.setPixmap(pixmap)
            self._tray.setIcon(QIcon(path))
        else:
            self._label.setText("🐾\n点击\n换皮")
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._label.setStyleSheet(
                "background: rgba(100,180,255,180); border-radius: 16px; "
                "color: white; font-size: 14px; font-weight: bold;"
            )

    def _apply_size(self, size: int):
        self._size = size
        self._config.set("pet_size", size)
        self.resize(size, size)
        self._label.resize(size, size)
        self._load_skin(self._config.get("current_skin"))

    def set_panel(self, panel):
        self._panel = panel

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._press_pos = event.globalPosition().toPoint()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
            if self._panel and self._panel.isVisible():
                self._reposition_panel()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.pos()
            self._config.set("window_x", pos.x())
            self._config.set("window_y", pos.y())
            self._drag_pos = QPoint()
            moved = (event.globalPosition().toPoint() - self._press_pos).manhattanLength()
            if moved < 5 and self._panel:
                self._toggle_panel()

    def _toggle_panel(self):
        if self._panel.isVisible():
            self._panel.hide()
        else:
            self._panel.show()
            self._panel.raise_()
            self._reposition_panel()

    def _reposition_panel(self):
        if not self._panel:
            return
        current_screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        screen = current_screen.availableGeometry()
        pet = self.pos()
        pw = self._panel.width()
        ph = self._panel.height()

        # 优先放右侧，放不下就放左侧
        x = pet.x() + self._size + 10
        if x + pw > screen.right():
            x = pet.x() - pw - 10

        # 顶部对齐桌宠，超出底部则上移
        y = pet.y()
        if y + ph > screen.bottom():
            y = screen.bottom() - ph

        # 保证不超出左边和顶部
        x = max(screen.left(), x)
        y = max(screen.top(), y)

        self._panel.move(x, y)

    def _show_context_menu(self, pos):
        menu = QMenu(self)

        size_menu = menu.addMenu("大小")
        for label, px in SIZES.items():
            action = size_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self._size == px)
            action.triggered.connect(lambda checked, p=px: self._apply_size(p))

        menu.addSeparator()
        hide_action = menu.addAction("隐藏（托盘）")
        hide_action.triggered.connect(self._hide_all)
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)

        menu.exec(pos)

    def reload_skin(self, path: str):
        self._config.set("current_skin", path)
        self._load_skin(path)
