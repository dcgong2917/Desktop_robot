import os
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QMenu
from config import Config


class PetWidget(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self._panel = None
        self._drag_pos = QPoint()
        self._setup_window()
        self._load_skin(config.get("current_skin"))

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(120, 120)
        x = self._config.get("window_x") or 100
        y = self._config.get("window_y") or 100
        self.move(x, y)

        self._label = QLabel(self)
        self._label.resize(120, 120)

    def _load_skin(self, path: str):
        if not path or not os.path.exists(path):
            path = "assets/default_pet.gif"
        if path.lower().endswith(".gif"):
            self._movie = QMovie(path)
            self._label.setMovie(self._movie)
            self._movie.start()
        else:
            pixmap = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio)
            self._label.setPixmap(pixmap)

    def set_panel(self, panel):
        self._panel = panel

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.pos()
            self._config.set("window_x", pos.x())
            self._config.set("window_y", pos.y())
            moved = (event.globalPosition().toPoint() - self._drag_pos - self.pos()).manhattanLength()
            if moved < 5 and self._panel:
                self._toggle_panel()

    def _toggle_panel(self):
        if self._panel.isVisible():
            self._panel.hide()
        else:
            pet_pos = self.pos()
            self._panel.move(pet_pos.x() + 130, pet_pos.y())
            self._panel.show()
            self._panel.raise_()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit)
        menu.exec(pos)

    def _quit(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def reload_skin(self, path: str):
        self._config.set("current_skin", path)
        self._load_skin(path)
