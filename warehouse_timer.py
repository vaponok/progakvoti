#!/usr/bin/env python3
# warehouse_timer.py - Простой трекер складов с таймерами

import sys
import json
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtGui, QtWidgets


class WarehouseTimerWidget(QtWidgets.QWidget):
    """Виджет для отслеживания складов с таймерами"""
    
    def __init__(self):
        super().__init__()
        self.warehouses = []
        self.settings = QtCore.QSettings("Vaponok", "WarehouseTimer")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timers)
        self.timer.start(1000)  # Обновление каждую секунду
        self.setup_ui()
        self.load_state()
        
    def setup_ui(self):
        self.setObjectName("warehouseTimerWidget")
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Заголовок
        header = QtWidgets.QLabel("⏱️ Таймеры складов")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #071422;
                padding: 12px;
                background: #ffffff;
                border: 3px solid #000;
                border-radius: 12px;
            }
        """)
        main_layout.addWidget(header)
        
        # Поле ввода для нового склада
        input_row = QtWidgets.QHBoxLayout()
        input_row.setSpacing(8)
        
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Название склада (например: Склад A)")
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 3px solid #000;
                border-radius: 12px;
                padding: 10px 14px;
                background: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 3px solid #0066FF;
            }
        """)
        input_row.addWidget(self.name_input, stretch=1)
        
        self.add_btn = QtWidgets.QPushButton("➕ Добавить склад")
        self.add_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.add_btn.setStyleSheet("""
            QPushButton {
                border-radius: 12px;
                padding: 10px 20px;
                font-weight: 700;
                color: white;
                border: 3px solid #000;
                background-color: #0066FF;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1a7bff;
            }
            QPushButton:pressed {
                background-color: #0047b3;
            }
        """)
        self.add_btn.clicked.connect(self.add_warehouse)
        input_row.addWidget(self.add_btn)
        
        main_layout.addLayout(input_row)
        
        # Скроллируемая область для складов
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.viewport().setAutoFillBackground(False)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: #ffffff;
            }
        """)
        
        self.warehouses_container = QtWidgets.QWidget()
        self.warehouses_container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border: 3px solid #000;
                border-radius: 12px;
            }
        """)
        self.warehouses_layout = QtWidgets.QVBoxLayout(self.warehouses_container)
        self.warehouses_layout.setSpacing(10)
        self.warehouses_layout.setContentsMargins(12, 12, 12, 12)
        self.warehouses_layout.addStretch()
        
        scroll.setWidget(self.warehouses_container)
        main_layout.addWidget(scroll, stretch=1)
        
        # Подключение Enter для добавления
        self.name_input.returnPressed.connect(self.add_warehouse)
        
    def add_warehouse(self):
        """Добавить новый склад"""
        name = self.name_input.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название склада!")
            return
            
        # Создаём таймер на 50 часов от текущего момента
        expire_time = datetime.now() + timedelta(hours=50)
        
        warehouse_data = {
            'name': name,
            'expire_time': expire_time.isoformat()
        }
        
        self.warehouses.append(warehouse_data)
        self.create_warehouse_widget(warehouse_data)
        self.name_input.clear()
        self.save_state()
        
    def create_warehouse_widget(self, data):
        """Создать виджет для склада"""
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 3px solid #000;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Название склада
        name_label = QtWidgets.QLabel(data['name'])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #071422;
                border: none;
                padding: 0;
                background: transparent;
            }
        """)
        name_label.setMinimumWidth(180)
        layout.addWidget(name_label)
        
        # Таймер
        timer_label = QtWidgets.QLabel()
        timer_label.setAlignment(QtCore.Qt.AlignCenter)
        timer_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #28a745;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 8px 16px;
                background: #e8f5e9;
                min-width: 150px;
            }
        """)
        layout.addWidget(timer_label)
        
        # Кнопка установки 50 часов
        refresh_btn = QtWidgets.QPushButton("⏰ 50ч")
        refresh_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        refresh_btn.setToolTip("Установить таймер на 50 часов от текущего момента")
        refresh_btn.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: 700;
                color: white;
                border: 3px solid #000;
                background-color: #28a745;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #34c759;
            }
            QPushButton:pressed {
                background-color: #1e8035;
            }
        """)
        refresh_btn.clicked.connect(lambda: self.set_warehouse_timer(data, timer_label))
        layout.addWidget(refresh_btn)
        
        # Кнопка удаления
        delete_btn = QtWidgets.QPushButton("🗑️")
        delete_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        delete_btn.setToolTip("Удалить склад")
        delete_btn.setFixedSize(40, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                padding: 6px;
                font-weight: 700;
                color: white;
                border: 3px solid #000;
                background-color: #dc3545;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff4757;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_warehouse(data, frame))
        layout.addWidget(delete_btn)
        
        # Сохраняем ссылку на label для обновления
        data['timer_label'] = timer_label
        data['frame'] = frame
        
        # Добавляем в layout (перед stretch)
        count = self.warehouses_layout.count()
        self.warehouses_layout.insertWidget(count - 1, frame)
        
        # Обновляем таймер сразу
        self.update_single_timer(data)
        
    def set_warehouse_timer(self, data, timer_label):
        """Установить таймер склада на 50 часов от текущего момента"""
        new_time = datetime.now() + timedelta(hours=50)
        data['expire_time'] = new_time.isoformat()
        self.update_single_timer(data)
        self.save_state()
        
    def delete_warehouse(self, data, frame):
        """Удалить склад"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Подтверждение',
            f"Удалить склад '{data['name']}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Удаляем из списка
            if data in self.warehouses:
                self.warehouses.remove(data)
            
            # Удаляем виджет
            frame.deleteLater()
            self.save_state()
            
    def update_timers(self):
        """Обновить все таймеры"""
        for data in self.warehouses:
            self.update_single_timer(data)
            
    def update_single_timer(self, data):
        """Обновить один таймер"""
        if 'timer_label' not in data:
            return
            
        expire_time = datetime.fromisoformat(data['expire_time'])
        now = datetime.now()
        delta = expire_time - now
        
        if delta.total_seconds() <= 0:
            # Время истекло
            data['timer_label'].setText("⚠️ ИСТЁК")
            data['timer_label'].setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 700;
                    color: #dc3545;
                    border: 2px solid #dc3545;
                    border-radius: 8px;
                    padding: 8px 16px;
                    background: #ffe6e6;
                    min-width: 150px;
                }
            """)
        else:
            # Форматируем оставшееся время
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            seconds = int(delta.total_seconds() % 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            data['timer_label'].setText(time_str)
            
            # Меняем цвет в зависимости от времени
            if hours > 48:
                # Более 48 часов - зелёный
                style = """
                    QLabel {
                        font-size: 16px;
                        font-weight: 700;
                        color: #28a745;
                        border: 2px solid #28a745;
                        border-radius: 8px;
                        padding: 8px 16px;
                        background: #e8f5e9;
                        min-width: 150px;
                    }
                """
            elif hours >= 5:
                # 5-48 часов - оранжевый
                style = """
                    QLabel {
                        font-size: 16px;
                        font-weight: 700;
                        color: #ff8c00;
                        border: 2px solid #ff8c00;
                        border-radius: 8px;
                        padding: 8px 16px;
                        background: #fff4e6;
                        min-width: 150px;
                    }
                """
            else:
                # Менее 5 часов - красный
                style = """
                    QLabel {
                        font-size: 16px;
                        font-weight: 700;
                        color: #dc3545;
                        border: 2px solid #dc3545;
                        border-radius: 8px;
                        padding: 8px 16px;
                        background: #ffe6e6;
                        min-width: 150px;
                    }
                """
            data['timer_label'].setStyleSheet(style)
            
    def save_state(self):
        """Сохранить состояние"""
        try:
            # Сохраняем только данные, без виджетов
            save_data = []
            for w in self.warehouses:
                save_data.append({
                    'name': w['name'],
                    'expire_time': w['expire_time']
                })
            self.settings.setValue("warehouses", json.dumps(save_data, ensure_ascii=False))
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            
    def load_state(self):
        """Загрузить состояние"""
        try:
            data = self.settings.value("warehouses", "")
            if data:
                loaded = json.loads(data)
                for item in loaded:
                    self.warehouses.append(item)
                    self.create_warehouse_widget(item)
        except Exception as e:
            print(f"Ошибка загрузки: {e}")


class WarehouseTimerWindow(QtWidgets.QMainWindow):
    """Отдельное окно для таймеров складов"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Таймеры складов - Foxhole")
        self.resize(700, 600)
        
        self.timer_widget = WarehouseTimerWidget()
        self.setCentralWidget(self.timer_widget)
        
        # Стили для главного окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
    def closeEvent(self, event):
        """Сохранить при закрытии"""
        self.timer_widget.save_state()
        super().closeEvent(event)


def main():
    """Запуск как отдельное приложение"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Шрифт
    font = QtGui.QFont("Inter", 10)
    app.setFont(font)
    
    window = WarehouseTimerWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()