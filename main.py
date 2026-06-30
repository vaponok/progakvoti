"""
Combined Foxhole Tools — главное окно с вкладками.

Объединяет:
- Распределитель ресурсов (resource_splitter.ResourceSplitter)
- Написание квоты (quota_writer.MainWindow)
- Таймеры складов (warehouse_timer.WarehouseTimerWidget)

Запуск: python main.py
"""
import os
import sys
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """Путь к ресурсу. Работает и в dev-режиме, и в PyInstaller-сборке."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# === Импорт виджетов ===
from resource_splitter import ResourceSplitter

try:
    from quota_writer import MainWindow as QuotaWriterWidget
except Exception as _e:
    logger.warning(f"quota_writer не загружен: {_e}")
    QuotaWriterWidget = None

try:
    from warehouse_timer import WarehouseTimerWidget
except Exception as _e:
    logger.warning(f"warehouse_timer не загружен: {_e}")
    WarehouseTimerWidget = None


# === TabBar с динамической шириной (как было в scanner_app) ===
class DynamicTabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index: int) -> QtCore.QSize:
        fm = self.fontMetrics()
        text = self.tabText(index)
        base_w = int(fm.horizontalAdvance(text) * 1.35) + 20
        if index == self.currentIndex():
            base_w += int(base_w * 0.20)
        base_h = fm.height() + 18
        return QtCore.QSize(base_w, base_h)


# === Кастомный заголовок окна с кнопками min/max/close ===
class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(64)
        self.setObjectName("customTitleBar")
        self.setStyleSheet("""
            QWidget#customTitleBar {
                background-color: #ffffff;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border: none;
            }
        """)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(28, 28)
        layout.addWidget(self.icon_label)

        layout.addStretch()

        def make_btn(text, tooltip):
            b = QtWidgets.QPushButton(text)
            b.setFixedSize(36, 28)
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            b.setToolTip(tooltip)
            b.setFocusPolicy(QtCore.Qt.NoFocus)
            b.setStyleSheet("""
                QPushButton {
                    border-radius: 6px;
                    padding: 0px;
                    font-weight: 700;
                    border: 3px solid #000;
                    background-color: #0066FF;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1a7bff;
                }
                QPushButton:pressed {
                    background-color: #0047b3;
                }
            """)
            return b

        self.min_btn = make_btn("─", "Свернуть")
        self.max_btn = make_btn("", "Развернуть")
        self.close_btn = make_btn("✕", "Закрыть")

        # Иконка квадрата для кнопки развернуть
        pix = QtGui.QPixmap(20, 20)
        pix.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pix)
        pen = QtGui.QPen(QtGui.QColor("white"), 2)
        painter.setPen(pen)
        painter.drawRect(2, 2, 16, 16)
        painter.end()
        icon = QtGui.QIcon(pix)
        self.max_btn.setIcon(icon)
        self.max_btn.setIconSize(QtCore.QSize(20, 20))

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        if self.parent:
            self.min_btn.clicked.connect(lambda: self.parent.showMinimized())
            self.max_btn.clicked.connect(self.toggle_max_restore)
            self.close_btn.clicked.connect(lambda: self.parent.close())

        self._is_max = False

    def toggle_max_restore(self):
        if not self.parent:
            return
        if self._is_max:
            self.parent.showNormal()
            self._is_max = False
        else:
            self.parent.showMaximized()
            self._is_max = True

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self._drag_pos = ev.globalPos()
            self._start_geom = self.parent.geometry()

    def mouseMoveEvent(self, ev):
        if hasattr(self, "_drag_pos") and ev.buttons() & QtCore.Qt.LeftButton:
            delta = ev.globalPos() - self._drag_pos
            new_pos = self._start_geom.topLeft() + delta
            self.parent.move(new_pos)


# === Главное окно приложения ===
class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combined Foxhole Tools")
        self.resize(1400, 1000)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.title_bar = TitleBar(self)

        # --- Вкладка 1: Распределитель ---
        self.splitter = ResourceSplitter()

        # Прокручиваемый контейнер для распределителя
        splitter_container = QtWidgets.QWidget()
        splitter_container.setObjectName("mainCanvas")
        sl = QtWidgets.QVBoxLayout(splitter_container)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(self.splitter)

        splitter_scroll = QtWidgets.QScrollArea()
        splitter_scroll.setWidgetResizable(True)
        splitter_scroll.setWidget(splitter_container)

        # --- Вкладка 2: Написание квоты ---
        if QuotaWriterWidget is not None:
            try:
                self.quota_widget = QuotaWriterWidget()
            except Exception as e:
                logger.exception(f"Ошибка создания QuotaWriter: {e}")
                self.quota_widget = QtWidgets.QWidget()
                l = QtWidgets.QVBoxLayout(self.quota_widget)
                l.addWidget(QtWidgets.QLabel(f"Ошибка при создании QuotaWriter:\n{e}"))
        else:
            self.quota_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.quota_widget)
            l.addWidget(QtWidgets.QLabel("quota_writer.py не найден или импорт не удался"))

        # --- Вкладка 3: Таймеры складов ---
        if WarehouseTimerWidget is not None:
            try:
                self.timer_widget = WarehouseTimerWidget()
            except Exception as e:
                logger.exception(f"Ошибка создания таймеров: {e}")
                self.timer_widget = QtWidgets.QWidget()
                l = QtWidgets.QVBoxLayout(self.timer_widget)
                l.addWidget(QtWidgets.QLabel(f"Ошибка при создании таймеров:\n{e}"))
        else:
            self.timer_widget = QtWidgets.QWidget()
            l = QtWidgets.QVBoxLayout(self.timer_widget)
            l.addWidget(QtWidgets.QLabel("warehouse_timer.py не найден"))

        # --- StackedWidget для переключения вкладок ---
        stacked = QtWidgets.QStackedWidget()
        stacked.addWidget(splitter_scroll)
        stacked.addWidget(self.quota_widget)
        stacked.addWidget(self.timer_widget)
        self.stacked = stacked

        # --- TabBar в title_bar ---
        dynamic_tb = DynamicTabBar()
        dynamic_tb.addTab("Распределитель")
        dynamic_tb.addTab("Написание квоты")
        dynamic_tb.addTab("Таймеры складов")
        dynamic_tb.currentChanged.connect(stacked.setCurrentIndex)
        dynamic_tb.currentChanged.connect(lambda idx: dynamic_tb.updateGeometry())

        layout = self.title_bar.layout()
        spacer = QtWidgets.QSpacerItem(50, 0, QtWidgets.QSizePolicy.Fixed,
                                       QtWidgets.QSizePolicy.Minimum)
        layout.insertItem(1, spacer)
        layout.insertWidget(2, dynamic_tb)

        # --- Центральный виджет ---
        central = QtWidgets.QWidget()
        central.setObjectName("centralWidget")
        central_layout = QtWidgets.QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.title_bar)
        central_layout.addWidget(stacked)
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
            }
            QWidget#centralWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 16px;
            }
            QWidget#customTitleBar {
                background-color: #ffffff;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border: none;
            }
            QStackedWidget {
                border: none;
                background: #ffffff;
                padding: 8px;
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            QTabBar::tab {
                background: #0066FF;
                color: white;
                border: 3px solid #000;
                border-bottom-color: #0066FF;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0047b3;
                border-bottom-color: #0047b3;
                font-weight: 800;
            }
            QWidget#mainCanvas {
                background: #ffffff;
                border: 3px solid #000;
                border-radius: 12px;
                padding: 8px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 18px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #0066FF;
                border: 3px solid #000;
                min-height: 30px;
                border-radius: 9px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 18px;
            }
            QScrollBar::handle:horizontal {
                background: #0066FF;
                border: 3px solid #000;
                min-width: 30px;
                border-radius: 9px;
            }
        """)

    def closeEvent(self, event):
        # Сохраняем состояние всех виджетов
        try:
            if hasattr(self, "splitter") and isinstance(self.splitter, ResourceSplitter):
                if hasattr(self.splitter, "save_settings"):
                    self.splitter.save_settings()
        except Exception as e:
            logger.warning(f"save_settings(splitter): {e}")

        try:
            if (hasattr(self, "quota_widget") and self.quota_widget is not None
                    and hasattr(self.quota_widget, "save_settings")):
                self.quota_widget.save_settings()
        except Exception as e:
            logger.warning(f"save_settings(quota_widget): {e}")

        try:
            if hasattr(self, "timer_widget") and hasattr(self.timer_widget, "save_state"):
                self.timer_widget.save_state()
        except Exception as e:
            logger.warning(f"save_state(timer_widget): {e}")

        super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QtGui.QFont("Inter", 10)
    app.setFont(font)

    # Иконка приложения
    app_icon = QtGui.QIcon(resource_path("icon.ico"))
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    else:
        logger.warning("Не удалось загрузить icon.ico")

    w = AppWindow()

    # Иконка в title_bar
    try:
        if hasattr(w, "title_bar") and getattr(w.title_bar, "icon_label", None) is not None:
            pix = QtGui.QPixmap(resource_path("icon.ico"))
            if not pix.isNull():
                pix = pix.scaled(28, 28, QtCore.Qt.KeepAspectRatio,
                                 QtCore.Qt.SmoothTransformation)
                w.title_bar.icon_label.setPixmap(pix)
    except Exception as e:
        logger.debug(f"Не удалось установить pixmap в title_bar: {e}")

    # Системный трей
    try:
        tray = QtWidgets.QSystemTrayIcon(app_icon, w)
        menu = QtWidgets.QMenu()
        show_action = menu.addAction("Открыть")
        quit_action = menu.addAction("Выход")
        show_action.triggered.connect(lambda: w.showNormal())
        quit_action.triggered.connect(lambda: app.quit())
        tray.setContextMenu(menu)
        tray.setToolTip("Combined Foxhole Tools")
        tray.show()
        w._sys_tray_icon = tray
    except Exception as e:
        logger.warning(f"Не удалось создать системный трей: {e}")

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
