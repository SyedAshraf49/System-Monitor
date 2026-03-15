"""
System Monitor Pro - Glassmorphism Edition
Professional system monitoring with stunning glassmorphism UI
Light blue and white color scheme
"""

import sys
import os
import json
import psutil
import threading
import sqlite3
import time
from datetime import datetime, timedelta
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *
import platform
import subprocess
import struct

# Optional GPU support
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Settings
SETTINGS_FILE = "monitor_settings.json"
DB_FILE = "system_monitor.db"
PROCESS_UPDATE_INTERVAL = 2
ALERT_CHECK_INTERVAL = 5  # Check alerts every 5 seconds


def get_cpu_info():
    """Get detailed CPU information"""
    try:
        cpu_info = {
            'brand': platform.processor(),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
        }
        
        freq = psutil.cpu_freq()
        if freq:
            cpu_info['current_freq'] = freq.current
            cpu_info['min_freq'] = freq.min
            cpu_info['max_freq'] = freq.max
        
        return cpu_info
    except:
        return {}

def get_memory_info():
    """Get detailed memory information"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    except:
        return {}

def get_disk_info():
    """Get detailed disk information"""
    try:
        disk = psutil.disk_usage('/')
        io = psutil.disk_io_counters()
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'read_count': io.read_count if io else 0,
            'write_count': io.write_count if io else 0,
            'read_bytes': io.read_bytes if io else 0,
            'write_bytes': io.write_bytes if io else 0
        }
    except:
        return {}

def get_network_info():
    """Get detailed network information"""
    try:
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errin': net.errin,
            'errout': net.errout,
            'dropin': net.dropin,
            'dropout': net.dropout
        }
    except:
        return {}

def get_system_uptime():
    """Get system uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return boot_time, uptime
    except:
        return None, None

def get_os_info():
    """Get detailed OS information"""
    try:
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation()
        }
    except:
        return {}


class GlassWidget(QWidget):
    """Base glass widget with glassmorphism effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Glass background
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 180))
        gradient.setColorAt(1, QColor(240, 248, 255, 150))
        
        painter.fillPath(path, gradient)
        
        # Border
        pen = QPen(QColor(200, 220, 240, 100), 2)
        painter.setPen(pen)
        painter.drawPath(path)


class CircularProgressGlass(QWidget):
    """Glassmorphism circular progress indicator with enhanced animations"""
    def __init__(self, title="", icon="", parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.title = title
        self.icon = icon
        self.subtitle = ""
        self.setMinimumSize(160, 180)
        self.setMaximumSize(160, 180)
        
        # Initialize animated value before creating animation
        self._value_animated = 0
        self._glow_intensity = 0
        
        # Main value animation
        self.animation = QPropertyAnimation(self, b"value_animated")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Glow animation
        self.glow_animation = QPropertyAnimation(self, b"glow_intensity")
        self.glow_animation.setDuration(1000)
        self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.glow_animation.setStartValue(0)
        self.glow_animation.setEndValue(50)
        
        # Animation group for simultaneous animations
        self.animation_group = QSequentialAnimationGroup()
        
    def get_value_animated(self):
        return self._value_animated
        
    def set_value_animated(self, value):
        self._value_animated = value
        self.update()
    
    def get_glow_intensity(self):
        return self._glow_intensity
    
    def set_glow_intensity(self, value):
        self._glow_intensity = value
        self.update()
        
    value_animated = pyqtProperty(float, get_value_animated, set_value_animated)
    glow_intensity = pyqtProperty(float, get_glow_intensity, set_glow_intensity)
        
    def setValue(self, value):
        self.value = max(0, min(value, self.max_value))
        self.animation.setStartValue(self._value_animated)
        self.animation.setEndValue(self.value)
        
        # Start glow animation
        self.glow_animation.setStartValue(0)
        self.glow_animation.setEndValue(50)
        
        self.animation.start()
        self.glow_animation.start()
        
    def setSubtitle(self, text):
        self.subtitle = text
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Drop shadow effect with glow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(QRectF(7, 7, width-14, height-14), 15, 15)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 15))
        
        # Glass background with enhanced gradient
        path = QPainterPath()
        path.addRoundedRect(QRectF(5, 5, width-10, height-10), 15, 15)
        
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(255, 255, 255, 240))
        gradient.setColorAt(0.5, QColor(248, 252, 255, 230))
        gradient.setColorAt(1, QColor(240, 248, 255, 220))
        painter.fillPath(path, gradient)
        
        # Enhanced border with gradient
        border_gradient = QLinearGradient(0, 0, 0, height)
        border_gradient.setColorAt(0, QColor(173, 216, 230, 200))
        border_gradient.setColorAt(1, QColor(135, 206, 250, 180))
        pen = QPen(QBrush(border_gradient), 2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Center circle area
        center_x = width / 2
        center_y = height / 2 - 10
        radius = 50
        
        # Outer glow effect with animation
        for i in range(3):
            glow_color = QColor(100, 149, 237, int(20 - i * 5 + self._glow_intensity * 0.2))
            painter.setPen(QPen(glow_color, 10 - i * 2))
            painter.drawEllipse(QPointF(center_x, center_y), radius + i * 2, radius + i * 2)
        
        # Background circle with subtle gradient
        bg_gradient = QRadialGradient(center_x, center_y, radius)
        bg_gradient.setColorAt(0, QColor(240, 248, 255))
        bg_gradient.setColorAt(1, QColor(230, 240, 250))
        painter.setBrush(bg_gradient)
        painter.setPen(QPen(QColor(220, 235, 245), 8))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Progress arc
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Determine color based on value with smooth transitions
        if self._value_animated < 50:
            color = QColor(100, 200, 255)  # Light blue
            glow_color = QColor(100, 200, 255, 50)
        elif self._value_animated < 75:
            color = QColor(30, 144, 255)  # Dodger blue
            glow_color = QColor(30, 144, 255, 50)
        elif self._value_animated < 90:
            color = QColor(255, 165, 0)  # Orange warning
            glow_color = QColor(255, 165, 0, 50)
        else:
            color = QColor(255, 69, 0)   # Red critical
            glow_color = QColor(255, 69, 0, 50)
            
        # Create gradient for progress
        progress_gradient = QConicalGradient(center_x, center_y, -90)
        progress_gradient.setColorAt(0, color.lighter(130))
        progress_gradient.setColorAt(0.5, color)
        progress_gradient.setColorAt(1, color.darker(110))
        
        # Draw progress arc with glow
        for i in range(2):
            pen = QPen(QBrush(glow_color if i == 0 else progress_gradient), 
                      12 if i == 0 else 10, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            span_angle = int(360 * 16 * self._value_animated / self.max_value)
            painter.drawArc(rect, 90 * 16, -span_angle)
        
        # Inner circle with enhanced glass effect
        inner_gradient = QRadialGradient(center_x, center_y - 5, radius - 15)
        inner_gradient.setColorAt(0, QColor(255, 255, 255, 250))
        inner_gradient.setColorAt(0.7, QColor(248, 252, 255, 240))
        inner_gradient.setColorAt(1, QColor(240, 248, 255, 230))
        painter.setBrush(inner_gradient)
        painter.setPen(QPen(QColor(200, 220, 240, 100), 1))
        painter.drawEllipse(QPointF(center_x, center_y), radius - 15, radius - 15)
        
        # Value text with shadow
        painter.setPen(QColor(200, 220, 240, 80))
        font = QFont("Segoe UI", 20, QFont.Bold)
        painter.setFont(font)
        text = f"{int(self._value_animated)}%"
        painter.drawText(QRectF(1, center_y - 14, width, 30), Qt.AlignCenter, text)
        
        painter.setPen(QColor(30, 60, 100))
        painter.drawText(QRectF(0, center_y - 15, width, 30), Qt.AlignCenter, text)
        
        # Title with enhanced styling
        painter.setPen(QColor(30, 144, 255))
        font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, height - 50, width, 20), Qt.AlignCenter, self.title)
        
        # Subtitle
        if self.subtitle:
            painter.setPen(QColor(100, 149, 237))
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(QRectF(0, height - 30, width, 20), Qt.AlignCenter, self.subtitle)


class InfoCardGlass(QFrame):
    """Glass information card with fade animations"""
    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumWidth(200)
        self._opacity = 1.0
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title with icon
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            title_layout.addWidget(icon_label)
            
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #4682B4;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Value label
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1E90FF;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel("")
        self.subtitle_label.setStyleSheet("""
            font-size: 10px;
            color: #6495ED;
        """)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
        
        # Fade-in animation
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = max(0, min(1, value))
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
        
    def setValue(self, value):
        self.value_label.setText(str(value))
        
    def setSubtitle(self, text):
        self.subtitle_label.setText(text)
        
    def start_fade_in(self):
        """Start fade-in animation"""
        if self.fade_animation.state() == QPropertyAnimation.Stopped:
            self.fade_animation.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Drop shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 12, 12)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 20))
        
        # Glass effect with enhanced gradient
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(0, 0, 0, 0), 12, 12)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 240))
        gradient.setColorAt(0.5, QColor(248, 252, 255, 230))
        gradient.setColorAt(1, QColor(240, 248, 255, 220))
        painter.fillPath(path, gradient)
        
        # Border with gradient
        border_gradient = QLinearGradient(0, 0, 0, self.height())
        border_gradient.setColorAt(0, QColor(173, 216, 230, 180))
        border_gradient.setColorAt(1, QColor(135, 206, 250, 150))
        pen = QPen(QBrush(border_gradient), 2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Accent line at top
        accent_path = QPainterPath()
        accent_path.addRoundedRect(QRectF(0, 0, self.width(), 4), 2, 2)
        accent_gradient = QLinearGradient(0, 0, self.width(), 0)
        accent_gradient.setColorAt(0, QColor(30, 144, 255, 0))
        accent_gradient.setColorAt(0.5, QColor(30, 144, 255, 200))
        accent_gradient.setColorAt(1, QColor(30, 144, 255, 0))
        painter.fillPath(accent_path, accent_gradient)


class AlertManager(QObject):
    """Manage system alerts and notifications"""
    alert_triggered = pyqtSignal(str, str, str)  # title, message, severity
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.alerts = {
            'cpu': {'enabled': True, 'threshold': 90, 'last_alert': 0},
            'memory': {'enabled': True, 'threshold': 90, 'last_alert': 0},
            'disk': {'enabled': True, 'threshold': 90, 'last_alert': 0},
            'temperature': {'enabled': True, 'threshold': 80, 'last_alert': 0}
        }
        self.alert_cooldown = 300  # 5 minutes between same alerts
        
    def check_alerts(self):
        """Check system metrics and trigger alerts"""
        current_time = time.time()
        
        # CPU Alert
        if self.alerts['cpu']['enabled']:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self.alerts['cpu']['threshold']:
                if current_time - self.alerts['cpu']['last_alert'] > self.alert_cooldown:
                    self.alert_triggered.emit(
                        "CPU Alert",
                        f"CPU usage is at {cpu_percent:.1f}%",
                        "warning"
                    )
                    self.alerts['cpu']['last_alert'] = current_time
        
        # Memory Alert
        if self.alerts['memory']['enabled']:
            mem = psutil.virtual_memory()
            if mem.percent > self.alerts['memory']['threshold']:
                if current_time - self.alerts['memory']['last_alert'] > self.alert_cooldown:
                    self.alert_triggered.emit(
                        "Memory Alert",
                        f"Memory usage is at {mem.percent:.1f}%",
                        "warning"
                    )
                    self.alerts['memory']['last_alert'] = current_time
        
        # Disk Alert
        if self.alerts['disk']['enabled']:
            disk = psutil.disk_usage('/')
            if disk.percent > self.alerts['disk']['threshold']:
                if current_time - self.alerts['disk']['last_alert'] > self.alert_cooldown:
                    self.alert_triggered.emit(
                        "Disk Alert",
                        f"Disk usage is at {disk.percent:.1f}%",
                        "warning"
                    )
                    self.alerts['disk']['last_alert'] = current_time
        
        # Temperature Alert (if available)
        if self.alerts['temperature']['enabled'] and hasattr(psutil, "sensors_temperatures"):
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > self.alerts['temperature']['threshold']:
                                if current_time - self.alerts['temperature']['last_alert'] > self.alert_cooldown:
                                    self.alert_triggered.emit(
                                        "Temperature Alert",
                                        f"{name} temperature is at {entry.current:.1f}°C",
                                        "critical"
                                    )
                                    self.alerts['temperature']['last_alert'] = current_time
                                    break
            except:
                pass
    
    def set_threshold(self, alert_type, threshold):
        """Set alert threshold"""
        if alert_type in self.alerts:
            self.alerts[alert_type]['threshold'] = threshold
    
    def toggle_alert(self, alert_type, enabled):
        """Enable/disable alert"""
        if alert_type in self.alerts:
            self.alerts[alert_type]['enabled'] = enabled


class ProcessWorker(QThread):
    """Worker thread for process monitoring"""
    processes_ready = pyqtSignal(list)
    
    def __init__(self, interval=PROCESS_UPDATE_INTERVAL, top_n=50, parent=None):
        super().__init__(parent)
        self.interval = interval
        self.top_n = top_n
        self._running = True
        
    def run(self):
        psutil.cpu_percent(interval=None)
        
        while self._running:
            processes = []
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                                 'status', 'create_time', 'num_threads', 'username']):
                    try:
                        info = proc.info
                        info['cpu_percent'] = info.get('cpu_percent') or 0.0
                        info['memory_percent'] = info.get('memory_percent') or 0.0
                        
                        if info['create_time']:
                            uptime = datetime.now() - datetime.fromtimestamp(info['create_time'])
                            info['uptime'] = str(uptime).split('.')[0]
                        else:
                            info['uptime'] = 'N/A'
                            
                        processes.append(info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                self.processes_ready.emit(processes[:self.top_n])
                
            except Exception as e:
                print(f"Process worker error: {e}")
                
            for _ in range(int(self.interval * 2)):
                if not self._running:
                    break
                time.sleep(0.5)
                
    def stop(self):
        self._running = False
        self.wait(2000)


class NetworkMonitorWorker(QThread):
    """Worker thread for network monitoring"""
    network_data = pyqtSignal(dict)
    
    def __init__(self, interval=1, parent=None):
        super().__init__(parent)
        self.interval = interval
        self._running = True
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        
    def run(self):
        while self._running:
            try:
                current_io = psutil.net_io_counters()
                current_time = time.time()
                elapsed = current_time - self.last_time
                
                if elapsed > 0:
                    upload_speed = (current_io.bytes_sent - self.last_io.bytes_sent) / elapsed
                    download_speed = (current_io.bytes_recv - self.last_io.bytes_recv) / elapsed
                    
                    data = {
                        'upload_speed': upload_speed,
                        'download_speed': download_speed,
                        'total_sent': current_io.bytes_sent,
                        'total_recv': current_io.bytes_recv,
                        'packets_sent': current_io.packets_sent,
                        'packets_recv': current_io.packets_recv
                    }
                    
                    self.network_data.emit(data)
                    
                self.last_io = current_io
                self.last_time = current_time
                
            except Exception as e:
                print(f"Network monitor error: {e}")
                
            time.sleep(self.interval)
            
    def stop(self):
        self._running = False
        self.wait(2000)


class SystemMonitorGlass(QMainWindow):
    """Main application with glassmorphism design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor Pro - Glassmorphism Edition")
        self.setGeometry(100, 50, 1400, 900)
        
        # Settings
        self.settings = self.load_settings()
        self.refresh_rate = self.settings.get("refresh_rate_ms", 1000)
        
        # Data structures
        self.max_history = 120
        self.cpu_history = deque(maxlen=self.max_history)
        self.memory_history = deque(maxlen=self.max_history)
        self.disk_history = deque(maxlen=self.max_history)
        self.network_up_history = deque(maxlen=self.max_history)
        self.network_down_history = deque(maxlen=self.max_history)
        
        # Tracking
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()
        
        # Database
        self.db_lock = threading.Lock()
        self.init_database()
        
        # Initialize
        psutil.cpu_percent(interval=None)
        
        # Build UI
        self.init_ui()
        self.apply_styles()
        
        # Workers
        self.process_worker = ProcessWorker(interval=PROCESS_UPDATE_INTERVAL, top_n=50)
        self.process_worker.processes_ready.connect(self.update_process_table)
        self.process_worker.start()
        
        self.network_worker = NetworkMonitorWorker(interval=1)
        self.network_worker.network_data.connect(self.update_network_data)
        self.network_worker.start()
        
        # Alert manager
        self.alert_manager = AlertManager()
        self.alert_manager.alert_triggered.connect(self.handle_alert)
        
        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(self.refresh_rate)
        
        self.chart_timer = QTimer()
        self.chart_timer.timeout.connect(self.update_charts)
        self.chart_timer.start(500)
        
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.check_alerts)
        self.alert_timer.start(ALERT_CHECK_INTERVAL * 1000)
        
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_settings(self):
        self.settings['refresh_rate_ms'] = self.refresh_rate
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
            
    def init_database(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                timestamp TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                memory_used INTEGER,
                disk_percent REAL,
                network_sent INTEGER,
                network_recv INTEGER
            )
        ''')
        self.conn.commit()
        
    def init_ui(self):
        # Central widget with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)
        
        central = QWidget()
        scroll.setWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Circular indicators (perfectly aligned)
        indicators_widget = self.create_circular_indicators()
        main_layout.addWidget(indicators_widget)
        
        # Info cards row
        cards_widget = self.create_info_cards()
        main_layout.addWidget(cards_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        
        self.create_overview_tab()
        self.create_process_tab()
        self.create_network_tab()
        self.create_storage_tab()
        self.create_performance_history_tab()
        self.create_alerts_tab()
        self.create_system_info_tab()
        
        # Menu
        self.create_menu()
        
    def create_header(self):
        """Create professional header with branding and system status with animations"""
        widget = QWidget()
        widget.setFixedHeight(100)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)
        
        # Top row with branding and controls
        top_row = QHBoxLayout()
        
        # Left side - Branding
        branding_layout = QHBoxLayout()
        
        # Logo/Icon with pulse animation
        logo_label = QLabel("⚡")
        logo_label.setStyleSheet("""
            font-size: 42px;
            color: #1E90FF;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(30, 144, 255, 30),
                stop:1 rgba(100, 149, 237, 30)
            );
            border-radius: 25px;
            padding: 5px 10px;
            min-width: 50px;
            max-width: 50px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Logo animation
        self.logo_animation = QPropertyAnimation(logo_label, b"minimumHeight")
        self.logo_animation.setDuration(800)
        self.logo_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.logo_animation.setLoopCount(-1)  # Infinite
        
        branding_layout.addWidget(logo_label)
        
        # Title with subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        
        title = QLabel("System Monitor Pro")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1E90FF;
            font-family: 'Segoe UI', Arial;
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Real-time Performance Analytics")
        subtitle.setStyleSheet("""
            font-size: 11px;
            color: #6495ED;
            font-weight: 500;
            margin-top: -2px;
        """)
        title_layout.addWidget(subtitle)
        
        branding_layout.addLayout(title_layout)
        branding_layout.addSpacing(20)
        top_row.addLayout(branding_layout)
        
        top_row.addStretch()
        
        # Right side - Status indicators and time
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        
        # Live indicator with animation
        self.status_indicator = QLabel("● LIVE")
        self.status_indicator.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #32CD32;
            background: rgba(50, 205, 50, 20);
            padding: 5px 12px;
            border-radius: 12px;
            border: 1px solid rgba(50, 205, 50, 100);
        """)
        status_layout.addWidget(self.status_indicator)
        
        # Separator
        sep = QLabel("|")
        sep.setStyleSheet("color: rgba(100, 149, 237, 100); font-size: 16px;")
        status_layout.addWidget(sep)
        
        # System time and date
        time_container = QVBoxLayout()
        time_container.setSpacing(0)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            font-size: 16px;
            color: #1E90FF;
            font-weight: bold;
        """)
        self.time_label.setAlignment(Qt.AlignRight)
        time_container.addWidget(self.time_label)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            font-size: 10px;
            color: #6495ED;
            font-weight: 500;
        """)
        self.date_label.setAlignment(Qt.AlignRight)
        time_container.addWidget(self.date_label)
        
        status_layout.addLayout(time_container)
        top_row.addLayout(status_layout)
        
        layout.addLayout(top_row)
        
        # Bottom row - Quick stats bar
        quick_stats = QHBoxLayout()
        quick_stats.setSpacing(20)
        
        self.quick_cpu_label = QLabel("CPU: --")
        self.quick_cpu_label.setStyleSheet("""
            font-size: 10px;
            color: #4682B4;
            font-weight: 600;
            padding: 3px 8px;
            background: rgba(70, 130, 180, 15);
            border-radius: 5px;
        """)
        quick_stats.addWidget(self.quick_cpu_label)
        
        self.quick_mem_label = QLabel("RAM: --")
        self.quick_mem_label.setStyleSheet("""
            font-size: 10px;
            color: #4682B4;
            font-weight: 600;
            padding: 3px 8px;
            background: rgba(70, 130, 180, 15);
            border-radius: 5px;
        """)
        quick_stats.addWidget(self.quick_mem_label)
        
        self.quick_disk_label = QLabel("DISK: --")
        self.quick_disk_label.setStyleSheet("""
            font-size: 10px;
            color: #4682B4;
            font-weight: 600;
            padding: 3px 8px;
            background: rgba(70, 130, 180, 15);
            border-radius: 5px;
        """)
        quick_stats.addWidget(self.quick_disk_label)
        
        self.quick_net_label = QLabel("NET: --")
        self.quick_net_label.setStyleSheet("""
            font-size: 10px;
            color: #4682B4;
            font-weight: 600;
            padding: 3px 8px;
            background: rgba(70, 130, 180, 15);
            border-radius: 5px;
        """)
        quick_stats.addWidget(self.quick_net_label)
        
        quick_stats.addStretch()
        layout.addLayout(quick_stats)
        
        # Add divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(173, 216, 230, 0),
                stop:0.5 rgba(173, 216, 230, 150),
                stop:1 rgba(173, 216, 230, 0)
            );
            max-height: 2px;
            border: none;
        """)
        layout.addWidget(divider)
        
        # Update time
        time_timer = QTimer(self)
        time_timer.timeout.connect(self.update_time)
        time_timer.start(1000)
        self.update_time()
        
        # Animate status indicator
        self.status_animation_timer = QTimer(self)
        self.status_animation_timer.timeout.connect(self.animate_status)
        self.status_animation_timer.start(1000)
        
        return widget
        
    def animate_status(self):
        """Animate the live status indicator"""
        current = self.status_indicator.styleSheet()
        if "color: #32CD32" in current:
            self.status_indicator.setStyleSheet("""
                font-size: 11px;
                font-weight: bold;
                color: #00FF00;
                background: rgba(0, 255, 0, 25);
                padding: 5px 12px;
                border-radius: 12px;
                border: 1px solid rgba(0, 255, 0, 120);
            """)
        else:
            self.status_indicator.setStyleSheet("""
                font-size: 11px;
                font-weight: bold;
                color: #32CD32;
                background: rgba(50, 205, 50, 20);
                padding: 5px 12px;
                border-radius: 12px;
                border: 1px solid rgba(50, 205, 50, 100);
            """)
        
    def update_time(self):
        """Update current time and date display"""
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        
    def create_circular_indicators(self):
        """Create perfectly aligned circular progress indicators"""
        widget = QWidget()
        widget.setFixedHeight(200)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(30)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add stretch before
        layout.addStretch()
        
        # CPU
        self.cpu_circle = CircularProgressGlass("CPU", "🖥️")
        layout.addWidget(self.cpu_circle)
        
        # Memory
        self.memory_circle = CircularProgressGlass("Memory", "💾")
        layout.addWidget(self.memory_circle)
        
        # Disk
        self.disk_circle = CircularProgressGlass("Disk", "💿")
        layout.addWidget(self.disk_circle)
        
        # GPU (if available)
        if GPU_AVAILABLE:
            self.gpu_circle = CircularProgressGlass("GPU", "🎮")
            layout.addWidget(self.gpu_circle)
        
        # Add stretch after
        layout.addStretch()
        
        return widget
        
    def create_info_cards(self):
        """Create information cards with fade-in animations"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addStretch()
        
        # Network Upload
        self.upload_card = InfoCardGlass("Upload", "⬆️")
        self.upload_card.setValue("0 KB/s")
        layout.addWidget(self.upload_card)
        self.upload_card.start_fade_in()
        
        # Network Download
        self.download_card = InfoCardGlass("Download", "⬇️")
        self.download_card.setValue("0 KB/s")
        layout.addWidget(self.download_card)
        self.download_card.start_fade_in()
        
        # Battery (if available)
        if hasattr(psutil, "sensors_battery") and psutil.sensors_battery():
            self.battery_card = InfoCardGlass("Battery", "🔋")
            self.battery_card.setValue("--")
            layout.addWidget(self.battery_card)
            self.battery_card.start_fade_in()
        
        # Temperature
        if hasattr(psutil, "sensors_temperatures"):
            self.temp_card = InfoCardGlass("Temperature", "🌡️")
            self.temp_card.setValue("-- °C")
            layout.addWidget(self.temp_card)
            self.temp_card.start_fade_in()
        
        # Processes
        self.process_card = InfoCardGlass("Processes", "⚙️")
        self.process_card.setValue("0")
        layout.addWidget(self.process_card)
        self.process_card.start_fade_in()
        
        # Uptime
        self.uptime_card = InfoCardGlass("Uptime", "⏱️")
        self.uptime_card.setValue("--")
        layout.addWidget(self.uptime_card)
        self.uptime_card.start_fade_in()
        
        layout.addStretch()
        
        return widget
        
    def create_overview_tab(self):
        """Create overview tab with charts"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Charts container
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        charts_layout.setSpacing(15)
        
        # CPU Chart
        self.cpu_chart = self.create_glass_chart("CPU Usage (%)")
        self.cpu_series = QLineSeries()
        self.cpu_series.setName("CPU %")
        pen = QPen(QColor(30, 144, 255), 3)
        self.cpu_series.setPen(pen)
        self.cpu_chart.addSeries(self.cpu_series)
        self.cpu_chart.createDefaultAxes()
        
        # Customize axes
        axis_x = self.cpu_chart.axes(Qt.Horizontal)[0]
        axis_x.setTitleText("Time (samples)")
        axis_x.setRange(0, self.max_history)
        axis_x.setLabelFormat("%d")
        
        axis_y = self.cpu_chart.axes(Qt.Vertical)[0]
        axis_y.setTitleText("Usage (%)")
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%d")
        
        self.style_chart_axes(self.cpu_chart)
        
        cpu_chart_view = QChartView(self.cpu_chart)
        cpu_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(cpu_chart_view, 0, 0)
        
        # Memory Chart
        self.memory_chart = self.create_glass_chart("Memory Usage (%)")
        self.memory_series = QLineSeries()
        self.memory_series.setName("Memory %")
        pen = QPen(QColor(100, 149, 237), 3)
        self.memory_series.setPen(pen)
        self.memory_chart.addSeries(self.memory_series)
        self.memory_chart.createDefaultAxes()
        
        # Customize axes
        axis_x = self.memory_chart.axes(Qt.Horizontal)[0]
        axis_x.setTitleText("Time (samples)")
        axis_x.setRange(0, self.max_history)
        axis_x.setLabelFormat("%d")
        
        axis_y = self.memory_chart.axes(Qt.Vertical)[0]
        axis_y.setTitleText("Usage (%)")
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%d")
        
        self.style_chart_axes(self.memory_chart)
        
        memory_chart_view = QChartView(self.memory_chart)
        memory_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(memory_chart_view, 0, 1)
        
        # Disk Chart
        self.disk_chart = self.create_glass_chart("Disk Usage (%)")
        self.disk_series = QLineSeries()
        self.disk_series.setName("Disk %")
        pen = QPen(QColor(70, 130, 180), 3)
        self.disk_series.setPen(pen)
        self.disk_chart.addSeries(self.disk_series)
        self.disk_chart.createDefaultAxes()
        
        # Customize axes
        axis_x = self.disk_chart.axes(Qt.Horizontal)[0]
        axis_x.setTitleText("Time (samples)")
        axis_x.setRange(0, self.max_history)
        axis_x.setLabelFormat("%d")
        
        axis_y = self.disk_chart.axes(Qt.Vertical)[0]
        axis_y.setTitleText("Usage (%)")
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%d")
        
        self.style_chart_axes(self.disk_chart)
        
        disk_chart_view = QChartView(self.disk_chart)
        disk_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(disk_chart_view, 1, 0)
        
        # Network Chart
        self.network_chart = self.create_glass_chart("Network Speed (KB/s)")
        
        self.net_up_series = QLineSeries()
        self.net_up_series.setName("Upload")
        pen = QPen(QColor(135, 206, 250), 3)
        self.net_up_series.setPen(pen)
        
        self.net_down_series = QLineSeries()
        self.net_down_series.setName("Download")
        pen = QPen(QColor(30, 144, 255), 3)
        self.net_down_series.setPen(pen)
        
        self.network_chart.addSeries(self.net_up_series)
        self.network_chart.addSeries(self.net_down_series)
        self.network_chart.createDefaultAxes()
        
        # Customize axes
        axis_x = self.network_chart.axes(Qt.Horizontal)[0]
        axis_x.setTitleText("Time (samples)")
        axis_x.setRange(0, self.max_history)
        axis_x.setLabelFormat("%d")
        
        axis_y = self.network_chart.axes(Qt.Vertical)[0]
        axis_y.setTitleText("Speed (KB/s)")
        axis_y.setRange(0, 100)  # Will be dynamically adjusted
        axis_y.setLabelFormat("%.1f")
        
        self.style_chart_axes(self.network_chart)
        
        network_chart_view = QChartView(self.network_chart)
        network_chart_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(network_chart_view, 1, 1)
        
        layout.addWidget(charts_widget)
        
        self.tabs.addTab(tab, "📊 Overview")
        
    def create_glass_chart(self, title):
        """Create a chart with glass styling"""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Styling
        chart.setBackgroundBrush(QBrush(QColor(255, 255, 255, 180)))
        chart.setBackgroundRoundness(15)
        chart.setTitleBrush(QBrush(QColor(30, 144, 255)))
        
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        chart.setTitleFont(title_font)
        
        # Legend styling
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.legend().setLabelColor(QColor(70, 130, 180))
        chart.legend().setBackgroundVisible(True)
        chart.legend().setBrush(QBrush(QColor(240, 248, 255, 200)))
        chart.legend().setPen(QPen(QColor(173, 216, 230, 100), 1))
        
        # Margins
        chart.setMargins(QMargins(10, 10, 10, 10))
        
        return chart
    
    def style_chart_axes(self, chart):
        """Apply styling to chart axes"""
        try:
            # Style all axes
            for axis in chart.axes():
                # Axis labels
                axis.setLabelsColor(QColor(70, 130, 180))
                axis.setLabelsFont(QFont("Segoe UI", 8))
                
                # Axis line
                axis_pen = QPen(QColor(173, 216, 230, 180), 2)
                axis.setLinePen(axis_pen)
                
                # Grid lines
                grid_pen = QPen(QColor(200, 220, 240, 100), 1, Qt.DotLine)
                axis.setGridLinePen(grid_pen)
                axis.setGridLineVisible(True)
                
                # Axis title
                axis.setTitleBrush(QBrush(QColor(30, 144, 255)))
                axis.setTitleFont(QFont("Segoe UI", 9, QFont.Bold))
        except Exception as e:
            print(f"Axis styling error: {e}")
        
    def create_process_tab(self):
        """Create process management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("color: #4682B4; font-weight: bold;")
        self.process_search = QLineEdit()
        self.process_search.setPlaceholderText("Filter processes...")
        self.process_search.textChanged.connect(self.filter_processes)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.request_process_refresh)
        
        kill_btn = QPushButton("❌ End Process")
        kill_btn.clicked.connect(self.kill_selected_process)
        
        toolbar.addWidget(search_label)
        toolbar.addWidget(self.process_search, 1)
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(kill_btn)
        
        layout.addLayout(toolbar)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(8)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "CPU %", "Memory %", "Status", 
            "Threads", "User", "Uptime"
        ])
        self.process_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.process_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.process_table.setSortingEnabled(True)
        self.process_table.horizontalHeader().setStretchLastSection(True)
        self.process_table.setAlternatingRowColors(True)
        
        # Column widths
        self.process_table.setColumnWidth(0, 80)
        self.process_table.setColumnWidth(1, 250)
        self.process_table.setColumnWidth(2, 80)
        self.process_table.setColumnWidth(3, 90)
        self.process_table.setColumnWidth(4, 100)
        self.process_table.setColumnWidth(5, 80)
        self.process_table.setColumnWidth(6, 120)
        
        layout.addWidget(self.process_table)
        
        self.tabs.addTab(tab, "⚙️ Processes")
        
    def create_network_tab(self):
        """Create network monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Network statistics
        stats_group = QGroupBox("Network Statistics")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(10)
        
        self.net_stats_labels = {}
        stats = [
            ("📤 Upload Speed:", "net_upload"),
            ("📥 Download Speed:", "net_download"),
            ("📊 Total Sent:", "net_sent"),
            ("📊 Total Received:", "net_recv"),
            ("📦 Packets Sent:", "net_packets_sent"),
            ("📦 Packets Received:", "net_packets_recv"),
        ]
        
        for i, (label, key) in enumerate(stats):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel("0")
            value_widget.setStyleSheet("color: #1E90FF; font-size: 13px;")
            self.net_stats_labels[key] = value_widget
            stats_layout.addWidget(label_widget, i, 0)
            stats_layout.addWidget(value_widget, i, 1)
            
        layout.addWidget(stats_group)
        
        # Network interfaces
        interfaces_group = QGroupBox("Network Interfaces")
        interfaces_layout = QVBoxLayout(interfaces_group)
        
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(4)
        self.interfaces_table.setHorizontalHeaderLabels(["Interface", "IPv4", "IPv6", "Status"])
        self.interfaces_table.horizontalHeader().setStretchLastSection(True)
        interfaces_layout.addWidget(self.interfaces_table)
        
        self.update_network_interfaces()
        
        layout.addWidget(interfaces_group)
        
        self.tabs.addTab(tab, "🌐 Network")
        
    def create_storage_tab(self):
        """Create storage tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Disk table
        disks_group = QGroupBox("Storage Devices")
        disks_layout = QVBoxLayout(disks_group)
        
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(6)
        self.disk_table.setHorizontalHeaderLabels([
            "Device", "Mount Point", "File System", "Total", "Used", "Free"
        ])
        self.disk_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.disk_table.horizontalHeader().setStretchLastSection(True)
        self.disk_table.setAlternatingRowColors(True)
        
        disks_layout.addWidget(self.disk_table)
        layout.addWidget(disks_group)
        
        self.update_disk_info()
        
        self.tabs.addTab(tab, "💾 Storage")
    
    def create_performance_history_tab(self):
        """Create performance history tab with statistics"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Date range selector
        range_widget = QWidget()
        range_layout = QHBoxLayout(range_widget)
        
        range_label = QLabel("📅 Time Range:")
        range_label.setStyleSheet("font-weight: bold; color: #4682B4;")
        range_layout.addWidget(range_label)
        
        self.history_range = QComboBox()
        self.history_range.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"])
        self.history_range.currentTextChanged.connect(self.load_history_data)
        range_layout.addWidget(self.history_range)
        
        range_layout.addStretch()
        
        stats_btn = QPushButton("📊 Show Statistics")
        stats_btn.clicked.connect(self.show_statistics)
        range_layout.addWidget(stats_btn)
        
        layout.addWidget(range_widget)
        
        # History table
        history_group = QGroupBox("Performance History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "CPU %", "Memory %", "Memory (GB)", 
            "Disk %", "Network Sent (MB)", "Network Recv (MB)"
        ])
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(True)
        
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_group)
        
        self.tabs.addTab(tab, "📈 History")
        
        # Load initial data
        self.load_history_data("Last Hour")
    
    def create_alerts_tab(self):
        """Create alerts configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Alerts info
        info_label = QLabel("⚠️ Configure system alerts to get notified when thresholds are exceeded")
        info_label.setStyleSheet("font-size: 13px; color: #4682B4; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Alert configurations
        alerts_group = QGroupBox("Alert Thresholds")
        alerts_layout = QGridLayout(alerts_group)
        alerts_layout.setSpacing(15)
        
        self.alert_widgets = {}
        alert_configs = [
            ("cpu", "🖥️ CPU Usage:", 90),
            ("memory", "💾 Memory Usage:", 90),
            ("disk", "💿 Disk Usage:", 90),
            ("temperature", "🌡️ Temperature:", 80)
        ]
        
        for row, (key, label, default) in enumerate(alert_configs):
            # Label
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4; font-size: 12px;")
            alerts_layout.addWidget(label_widget, row, 0)
            
            # Enable checkbox
            enable_check = QCheckBox("Enable")
            enable_check.setChecked(True)
            enable_check.setStyleSheet("color: #1E90FF;")
            alerts_layout.addWidget(enable_check, row, 1)
            
            # Threshold slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(50)
            slider.setMaximum(100)
            slider.setValue(default)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: rgba(173, 216, 230, 150);
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #1E90FF;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
            """)
            alerts_layout.addWidget(slider, row, 2)
            
            # Value label
            value_label = QLabel(f"{default}%")
            value_label.setStyleSheet("color: #1E90FF; font-weight: bold; min-width: 45px;")
            value_label.setAlignment(Qt.AlignCenter)
            alerts_layout.addWidget(value_label, row, 3)
            
            # Connect slider to label
            slider.valueChanged.connect(
                lambda val, lbl=value_label: lbl.setText(f"{val}%")
            )
            
            self.alert_widgets[key] = {
                'enable': enable_check,
                'slider': slider,
                'label': value_label
            }
        
        layout.addWidget(alerts_group)
        
        # Test alert button
        test_btn = QPushButton("🔔 Test Alert System")
        test_btn.clicked.connect(self.test_alert)
        test_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30, 144, 255, 180);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(30, 144, 255, 220);
            }
        """)
        layout.addWidget(test_btn)
        
        # Alert log
        log_group = QGroupBox("Recent Alerts")
        log_layout = QVBoxLayout(log_group)
        
        self.alert_log = QTextEdit()
        self.alert_log.setReadOnly(True)
        self.alert_log.setMaximumHeight(150)
        self.alert_log.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 200);
                border: 2px solid rgba(173, 216, 230, 150);
                border-radius: 8px;
                padding: 10px;
                color: #2C3E50;
            }
        """)
        log_layout.addWidget(self.alert_log)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "🔔 Alerts")
        
    def create_system_info_tab(self):
        """Create system information tab with comprehensive specs"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        scroll.setWidget(content)
        main_layout = QVBoxLayout(content)
        
        # Get all system info
        os_info = get_os_info()
        cpu_info = get_cpu_info()
        mem_info = get_memory_info()
        disk_info = get_disk_info()
        boot_time, uptime = get_system_uptime()
        
        # Operating System Section
        os_group = QGroupBox("🖥️ Operating System")
        os_layout = QFormLayout(os_group)
        
        specs = [
            ("System:", os_info.get('system', 'N/A')),
            ("Release:", os_info.get('release', 'N/A')),
            ("Version:", os_info.get('version', 'N/A')[:50] + "..."),
            ("Architecture:", os_info.get('architecture', 'N/A')),
            ("Hostname:", os_info.get('hostname', 'N/A')),
            ("Boot Time:", boot_time.strftime("%Y-%m-%d %H:%M:%S") if boot_time else "N/A"),
            ("System Uptime:", self.format_uptime(uptime) if uptime else "N/A"),
        ]
        
        for label, value in specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New';")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            os_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(os_group)
        
        # Processor Section
        cpu_group = QGroupBox("⚙️ Processor")
        cpu_layout = QFormLayout(cpu_group)
        
        cpu_specs = [
            ("Brand:", cpu_info.get('brand', 'N/A')[:60]),
            ("Physical Cores:", str(cpu_info.get('cores_physical', 'N/A'))),
            ("Logical Cores:", str(cpu_info.get('cores_logical', 'N/A'))),
            ("Current Frequency:", f"{cpu_info.get('current_freq', 0):.0f} MHz"),
            ("Min Frequency:", f"{cpu_info.get('min_freq', 0):.0f} MHz"),
            ("Max Frequency:", f"{cpu_info.get('max_freq', 0):.0f} MHz"),
            ("Base Speed:", f"{cpu_info.get('max_freq', 0) / 1000:.2f} GHz"),
        ]
        
        for label, value in cpu_specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New';")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            cpu_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(cpu_group)
        
        # Memory Section
        mem_group = QGroupBox("💾 Memory")
        mem_layout = QFormLayout(mem_group)
        
        mem_specs = [
            ("Total RAM:", self.format_bytes(mem_info.get('total', 0))),
            ("Available:", self.format_bytes(mem_info.get('available', 0))),
            ("Used:", self.format_bytes(mem_info.get('used', 0))),
            ("Usage Percentage:", f"{mem_info.get('percent', 0):.1f}%"),
            ("Total Swap:", self.format_bytes(mem_info.get('swap_total', 0))),
            ("Swap Used:", self.format_bytes(mem_info.get('swap_used', 0))),
            ("Swap Free:", self.format_bytes(mem_info.get('swap_free', 0))),
            ("Swap Usage:", f"{mem_info.get('swap_percent', 0):.1f}%"),
        ]
        
        for label, value in mem_specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New';")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            mem_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(mem_group)
        
        # Storage Section
        storage_group = QGroupBox("💿 Storage")
        storage_layout = QFormLayout(storage_group)
        
        storage_specs = [
            ("Total Disk:", self.format_bytes(disk_info.get('total', 0))),
            ("Used Space:", self.format_bytes(disk_info.get('used', 0))),
            ("Free Space:", self.format_bytes(disk_info.get('free', 0))),
            ("Usage Percentage:", f"{disk_info.get('percent', 0):.1f}%"),
            ("Read Operations:", f"{disk_info.get('read_count', 0):,}"),
            ("Write Operations:", f"{disk_info.get('write_count', 0):,}"),
            ("Total Bytes Read:", self.format_bytes(disk_info.get('read_bytes', 0))),
            ("Total Bytes Written:", self.format_bytes(disk_info.get('write_bytes', 0))),
        ]
        
        for label, value in storage_specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New';")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            storage_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(storage_group)
        
        # Network Section
        net_info = get_network_info()
        net_group = QGroupBox("🌐 Network")
        net_layout = QFormLayout(net_group)
        
        net_specs = [
            ("Bytes Sent:", self.format_bytes(net_info.get('bytes_sent', 0))),
            ("Bytes Received:", self.format_bytes(net_info.get('bytes_recv', 0))),
            ("Packets Sent:", f"{net_info.get('packets_sent', 0):,}"),
            ("Packets Received:", f"{net_info.get('packets_recv', 0):,}"),
            ("Errors In:", f"{net_info.get('errin', 0):,}"),
            ("Errors Out:", f"{net_info.get('errout', 0):,}"),
            ("Dropped In:", f"{net_info.get('dropin', 0):,}"),
            ("Dropped Out:", f"{net_info.get('dropout', 0):,}"),
        ]
        
        for label, value in net_specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New';")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            net_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(net_group)
        
        # Python Environment Section
        python_group = QGroupBox("🐍 Python Environment")
        python_layout = QFormLayout(python_group)
        
        python_specs = [
            ("Implementation:", os_info.get('python_implementation', 'N/A')),
            ("Version:", os_info.get('python_version', 'N/A')),
            ("Executable:", sys.executable),
        ]
        
        for label, value in python_specs:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #4682B4;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1E90FF; font-family: 'Courier New'; word-wrap: break-word;")
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value_widget.setWordWrap(True)
            python_layout.addRow(label_widget, value_widget)
        
        main_layout.addWidget(python_group)
        
        main_layout.addStretch()
        
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "ℹ️ System Info")
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def format_uptime(self, td):
        """Format timedelta to uptime string"""
        if not td:
            return "N/A"
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        seconds = td.seconds % 60
        return f"{days}d {hours}h {minutes}m {seconds}s"
        
    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        clear_action = QAction("Clear History", self)
        clear_action.triggered.connect(self.clear_history)
        tools_menu.addAction(clear_action)
        
        # Quick Actions menu
        actions_menu = menubar.addMenu("Quick Actions")
        
        task_mgr_action = QAction("Open Task Manager", self)
        task_mgr_action.triggered.connect(self.open_task_manager)
        actions_menu.addAction(task_mgr_action)
        
        resource_mon_action = QAction("Resource Monitor", self)
        resource_mon_action.triggered.connect(self.open_resource_monitor)
        actions_menu.addAction(resource_mon_action)
        
        actions_menu.addSeparator()
        
        cmd_action = QAction("Command Prompt", self)
        cmd_action.triggered.connect(self.open_cmd)
        actions_menu.addAction(cmd_action)
        
        powershell_action = QAction("PowerShell", self)
        powershell_action.triggered.connect(self.open_powershell)
        actions_menu.addAction(powershell_action)
        
        actions_menu.addSeparator()
        
        screenshot_action = QAction("Take Screenshot", self)
        screenshot_action.triggered.connect(self.take_screenshot)
        actions_menu.addAction(screenshot_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def apply_styles(self):
        """Apply professional glassmorphism styles"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E8F4F8,
                    stop:0.3 #F0F8FF,
                    stop:0.7 #F8FCFF,
                    stop:1 #FFFFFF
                );
            }
            
            QWidget {
                font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            /* Enhanced Tab Widget */
            QTabWidget::pane {
                border: 2px solid rgba(173, 216, 230, 150);
                border-radius: 12px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 240),
                    stop:1 rgba(248, 252, 255, 230)
                );
                top: -1px;
            }
            
            QTabBar::tab {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 248, 255, 200),
                    stop:1 rgba(230, 242, 250, 180)
                );
                border: 2px solid rgba(173, 216, 230, 120);
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 20px;
                margin-right: 3px;
                color: #4682B4;
                font-weight: 600;
                font-size: 12px;
            }
            
            QTabBar::tab:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(173, 216, 230, 180),
                    stop:1 rgba(135, 206, 250, 160)
                );
                color: #1E90FF;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 200),
                    stop:1 rgba(65, 105, 225, 220)
                );
                color: white;
                border-color: rgba(30, 144, 255, 200);
                font-weight: bold;
            }
            
            /* Enhanced Group Box */
            QGroupBox {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 240),
                    stop:1 rgba(248, 252, 255, 230)
                );
                border: 2px solid rgba(173, 216, 230, 150);
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 18px;
                font-weight: bold;
                color: #4682B4;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 5px 15px;
                color: #1E90FF;
                font-size: 14px;
                font-weight: bold;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 144, 255, 20),
                    stop:0.5 rgba(30, 144, 255, 40),
                    stop:1 rgba(30, 144, 255, 20)
                );
                border-radius: 8px;
            }
            
            /* Enhanced Table Widget */
            QTableWidget {
                background: rgba(255, 255, 255, 240);
                alternate-background-color: rgba(248, 252, 255, 230);
                border: 2px solid rgba(173, 216, 230, 150);
                border-radius: 10px;
                gridline-color: rgba(173, 216, 230, 100);
                color: #2C3E50;
                selection-background-color: rgba(30, 144, 255, 180);
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(173, 216, 230, 50);
            }
            
            QTableWidget::item:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 144, 255, 160),
                    stop:1 rgba(65, 105, 225, 180)
                );
                color: white;
                font-weight: 600;
            }
            
            QTableWidget::item:hover {
                background: rgba(173, 216, 230, 100);
            }
                background: rgba(30, 144, 255, 180);
                color: white;
            }
            
            /* Enhanced Header Section */
            QHeaderView::section {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(173, 216, 230, 220),
                    stop:1 rgba(135, 206, 250, 200)
                );
                color: #2C3E50;
                padding: 10px;
                border: none;
                border-right: 1px solid rgba(173, 216, 230, 120);
                border-bottom: 2px solid rgba(30, 144, 255, 150);
                font-weight: bold;
                font-size: 11px;
            }
            
            QHeaderView::section:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 150),
                    stop:1 rgba(65, 105, 225, 130)
                );
                color: white;
            }
            
            /* Enhanced Buttons */
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 220),
                    stop:1 rgba(65, 105, 225, 240)
                );
                color: white;
                border: 2px solid rgba(30, 144, 255, 180);
                padding: 10px 24px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(65, 105, 225, 240),
                    stop:1 rgba(30, 144, 255, 255)
                );
                border: 2px solid rgba(65, 105, 225, 220);
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 0, 139, 240),
                    stop:1 rgba(25, 25, 112, 255)
                );
                padding-top: 12px;
                padding-bottom: 8px;
            }
            
            QPushButton:disabled {
                background: rgba(200, 200, 200, 150);
                color: rgba(100, 100, 100, 150);
                border: 2px solid rgba(150, 150, 150, 100);
            }
            
            /* Enhanced Line Edit */
            QLineEdit {
                background: rgba(255, 255, 255, 240);
                border: 2px solid rgba(173, 216, 230, 180);
                padding: 10px 12px;
                border-radius: 10px;
                color: #2C3E50;
                font-size: 12px;
                selection-background-color: rgba(30, 144, 255, 150);
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(30, 144, 255, 220);
                background: rgba(255, 255, 255, 255);
                box-shadow: 0 0 10px rgba(30, 144, 255, 50);
            }
            
            QLineEdit:hover {
                border: 2px solid rgba(100, 149, 237, 200);
            }
            
            /* Enhanced Combo Box */
            QComboBox {
                background: rgba(255, 255, 255, 240);
                border: 2px solid rgba(173, 216, 230, 180);
                padding: 8px 12px;
                border-radius: 10px;
                color: #2C3E50;
                font-size: 12px;
                min-width: 120px;
            }
            
            QComboBox:hover {
                border: 2px solid rgba(100, 149, 237, 200);
                background: rgba(255, 255, 255, 255);
            }
            
            QComboBox:focus {
                border: 2px solid rgba(30, 144, 255, 220);
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4682B4;
                margin-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background: rgba(255, 255, 255, 250);
                border: 2px solid rgba(30, 144, 255, 180);
                border-radius: 8px;
                selection-background-color: rgba(30, 144, 255, 180);
                selection-color: white;
                padding: 5px;
            }
            
            /* Enhanced Spin Box */
            QSpinBox {
                background: rgba(255, 255, 255, 240);
                border: 2px solid rgba(173, 216, 230, 180);
                padding: 8px 12px;
                border-radius: 10px;
                color: #2C3E50;
                font-size: 12px;
            }
            
            QSpinBox:focus {
                border: 2px solid rgba(30, 144, 255, 220);
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(173, 216, 230, 150);
                border: none;
                border-radius: 5px;
                width: 20px;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: rgba(30, 144, 255, 180);
            }
            
            /* Enhanced Check Box */
            QCheckBox {
                color: #2C3E50;
                font-size: 12px;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(173, 216, 230, 180);
                border-radius: 6px;
                background: rgba(255, 255, 255, 240);
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid rgba(30, 144, 255, 200);
                background: rgba(240, 248, 255, 255);
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 144, 255, 220),
                    stop:1 rgba(65, 105, 225, 240)
                );
                border: 2px solid rgba(30, 144, 255, 220);
            }
            
            QTabWidget::pane {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 200),
                    stop:1 rgba(240, 248, 255, 180)
                );
                border: 2px solid rgba(173, 216, 230, 120);
                border-radius: 12px;
                padding: 10px;
            }
            
            QTabBar::tab {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 248, 255, 200),
                    stop:1 rgba(230, 240, 255, 180)
                );
                color: #4682B4;
                padding: 10px 20px;
                border: 2px solid rgba(173, 216, 230, 100);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 200),
                    stop:1 rgba(65, 105, 225, 180)
                );
                color: white;
                border: 2px solid rgba(30, 144, 255, 150);
                border-bottom: none;
            }
            
            QTabBar::tab:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(135, 206, 250, 200),
                    stop:1 rgba(100, 149, 237, 180)
                );
            }
            
            /* Enhanced Menu Bar */
            QMenuBar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 252, 255, 250),
                    stop:1 rgba(240, 248, 255, 240)
                );
                color: #2C3E50;
                border-bottom: 3px solid rgba(30, 144, 255, 100);
                font-weight: 600;
                font-size: 12px;
                padding: 5px;
            }
            
            QMenuBar::item {
                padding: 10px 18px;
                background: transparent;
                border-radius: 8px;
                margin: 2px;
            }
            
            QMenuBar::item:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(173, 216, 230, 150),
                    stop:1 rgba(135, 206, 250, 130)
                );
                color: #1E90FF;
            }
            
            QMenuBar::item:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 180),
                    stop:1 rgba(65, 105, 225, 200)
                );
                color: white;
            }
            
            /* Enhanced Menu Dropdown */
            QMenu {
                background: rgba(255, 255, 255, 250);
                border: 2px solid rgba(30, 144, 255, 150);
                border-radius: 12px;
                padding: 8px;
            }
            
            QMenu::item {
                padding: 10px 35px;
                border-radius: 8px;
                color: #2C3E50;
                font-size: 12px;
                margin: 2px;
            }
            
            QMenu::item:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(173, 216, 230, 150),
                    stop:1 rgba(135, 206, 250, 180)
                );
                color: #1E90FF;
            }
            
            QMenu::item:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 144, 255, 200),
                    stop:1 rgba(65, 105, 225, 220)
                );
                color: white;
                font-weight: 600;
            }
            
            QMenu::separator {
                height: 2px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(173, 216, 230, 0),
                    stop:0.5 rgba(173, 216, 230, 150),
                    stop:1 rgba(173, 216, 230, 0)
                );
                margin: 5px 10px;
            }
            
            /* Enhanced Scrollbar */
            QScrollBar:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(240, 248, 255, 200),
                    stop:1 rgba(230, 242, 250, 180)
                );
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 144, 255, 200),
                    stop:1 rgba(100, 149, 237, 220)
                );
                border-radius: 7px;
                min-height: 30px;
                border: 1px solid rgba(30, 144, 255, 100);
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(65, 105, 225, 230),
                    stop:1 rgba(30, 144, 255, 250)
                );
            }
            
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 0, 139, 240),
                    stop:1 rgba(25, 25, 112, 255)
                );
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* Enhanced Text Edit */
            QTextEdit {
                background: rgba(255, 255, 255, 240);
                border: 2px solid rgba(173, 216, 230, 150);
                border-radius: 10px;
                padding: 10px;
                color: #2C3E50;
                font-size: 12px;
                selection-background-color: rgba(30, 144, 255, 150);
            }
            
            QTextEdit:focus {
                border: 2px solid rgba(30, 144, 255, 220);
            }
            
            /* Enhanced Slider */
            QSlider::groove:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(230, 242, 250, 200),
                    stop:1 rgba(220, 235, 245, 180)
                );
                height: 10px;
                border-radius: 5px;
                border: 1px solid rgba(173, 216, 230, 120);
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 144, 255, 230),
                    stop:1 rgba(65, 105, 225, 250)
                );
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid rgba(30, 144, 255, 180);
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(65, 105, 225, 250),
                    stop:1 rgba(30, 144, 255, 255)
                );
                width: 22px;
                margin: -7px 0;
            }
        """)
        
    def update_data(self):
        """Update system data and quick stats"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_circle.setValue(cpu_percent)
            self.cpu_circle.setSubtitle(f"{psutil.cpu_count()} cores")
            self.cpu_history.append(cpu_percent)
            self.quick_cpu_label.setText(f"CPU: {cpu_percent:.0f}%")
            
            # Memory
            mem = psutil.virtual_memory()
            self.memory_circle.setValue(mem.percent)
            self.memory_circle.setSubtitle(f"{mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB")
            self.memory_history.append(mem.percent)
            self.quick_mem_label.setText(f"RAM: {mem.percent:.0f}%")
            
            # Disk
            disk = psutil.disk_usage('/')
            self.disk_circle.setValue(disk.percent)
            self.disk_circle.setSubtitle(f"{disk.used/(1024**3):.0f}/{disk.total/(1024**3):.0f} GB")
            self.disk_history.append(disk.percent)
            self.quick_disk_label.setText(f"DISK: {disk.percent:.0f}%")
            
            # GPU
            if GPU_AVAILABLE and hasattr(self, 'gpu_circle'):
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        self.gpu_circle.setValue(gpu.load * 100)
                        self.gpu_circle.setSubtitle(f"{gpu.temperature}°C")
                except:
                    pass
            
            # Temperature
            if hasattr(psutil, "sensors_temperatures") and hasattr(self, 'temp_card'):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                temp = entries[0].current
                                self.temp_card.setValue(f"{temp:.1f}°C")
                                break
                except:
                    pass
            
            # Battery
            if hasattr(psutil, "sensors_battery") and hasattr(self, 'battery_card'):
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        plugged = "⚡ " if battery.power_plugged else ""
                        self.battery_card.setValue(f"{plugged}{percent:.0f}%")
                        if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                            hours = battery.secsleft // 3600
                            minutes = (battery.secsleft % 3600) // 60
                            self.battery_card.setSubtitle(f"{hours}h {minutes}m left")
                        elif battery.power_plugged:
                            self.battery_card.setSubtitle("Charging")
                        else:
                            self.battery_card.setSubtitle("")
                except:
                    pass
            
            # Process count
            self.process_card.setValue(str(len(psutil.pids())))
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours = uptime.seconds // 3600
            self.uptime_card.setValue(f"{days}d {hours}h")
            
        except Exception as e:
            print(f"Update error: {e}")
            
    def update_charts(self):
        """Update charts"""
        try:
            # CPU
            self.cpu_series.clear()
            for i, value in enumerate(self.cpu_history):
                self.cpu_series.append(i, value)
            
            # Memory
            self.memory_series.clear()
            for i, value in enumerate(self.memory_history):
                self.memory_series.append(i, value)
            
            # Disk
            self.disk_series.clear()
            for i, value in enumerate(self.disk_history):
                self.disk_series.append(i, value)
            
            # Network - with dynamic Y-axis
            self.net_up_series.clear()
            max_up = 0
            for i, value in enumerate(self.network_up_history):
                self.net_up_series.append(i, value)
                max_up = max(max_up, value)
            
            self.net_down_series.clear()
            max_down = 0
            for i, value in enumerate(self.network_down_history):
                self.net_down_series.append(i, value)
                max_down = max(max_down, value)
            
            # Dynamically adjust network Y-axis
            max_speed = max(max_up, max_down, 10)  # Minimum 10 KB/s
            if len(self.network_chart.axes(Qt.Vertical)) > 0:
                axis_y = self.network_chart.axes(Qt.Vertical)[0]
                axis_y.setRange(0, max_speed * 1.1)  # Add 10% padding
                
        except Exception as e:
            print(f"Chart update error: {e}")
            
    def update_network_data(self, data):
        """Update network data and quick stats"""
        try:
            # Update cards
            self.upload_card.setValue(f"{data['upload_speed']/1024:.1f} KB/s")
            self.download_card.setValue(f"{data['download_speed']/1024:.1f} KB/s")
            
            # Update quick stats
            total_speed = (data['upload_speed'] + data['download_speed']) / 1024
            if total_speed < 1024:
                self.quick_net_label.setText(f"NET: {total_speed:.0f} KB/s")
            else:
                self.quick_net_label.setText(f"NET: {total_speed/1024:.1f} MB/s")
            
            # Update stats
            self.net_stats_labels['net_upload'].setText(f"{data['upload_speed']/1024:.2f} KB/s")
            self.net_stats_labels['net_download'].setText(f"{data['download_speed']/1024:.2f} KB/s")
            self.net_stats_labels['net_sent'].setText(f"{data['total_sent']/(1024**3):.2f} GB")
            self.net_stats_labels['net_recv'].setText(f"{data['total_recv']/(1024**3):.2f} GB")
            self.net_stats_labels['net_packets_sent'].setText(f"{data['packets_sent']:,}")
            self.net_stats_labels['net_packets_recv'].setText(f"{data['packets_recv']:,}")
            
            # Add to history
            self.network_up_history.append(data['upload_speed']/1024)
            self.network_down_history.append(data['download_speed']/1024)
            
        except Exception as e:
            print(f"Network update error: {e}")
            
    def update_network_interfaces(self):
        """Update network interfaces table"""
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            self.interfaces_table.setRowCount(len(addrs))
            
            for row, (name, addresses) in enumerate(addrs.items()):
                # Interface name
                self.interfaces_table.setItem(row, 0, QTableWidgetItem(name))
                
                # Get IPv4 and IPv6
                ipv4 = ipv6 = "N/A"
                for addr in addresses:
                    if addr.family == 2:  # AF_INET
                        ipv4 = addr.address
                    elif addr.family == 23:  # AF_INET6
                        ipv6 = addr.address[:20] + "..."
                
                self.interfaces_table.setItem(row, 1, QTableWidgetItem(ipv4))
                self.interfaces_table.setItem(row, 2, QTableWidgetItem(ipv6))
                
                # Status
                status = "Up" if name in stats and stats[name].isup else "Down"
                status_item = QTableWidgetItem(status)
                if status == "Up":
                    status_item.setForeground(QColor(30, 144, 255))
                self.interfaces_table.setItem(row, 3, status_item)
                
        except Exception as e:
            print(f"Network interfaces error: {e}")
            
    def update_disk_info(self):
        """Update disk information"""
        try:
            partitions = psutil.disk_partitions()
            self.disk_table.setRowCount(len(partitions))
            
            for row, partition in enumerate(partitions):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    self.disk_table.setItem(row, 0, QTableWidgetItem(partition.device))
                    self.disk_table.setItem(row, 1, QTableWidgetItem(partition.mountpoint))
                    self.disk_table.setItem(row, 2, QTableWidgetItem(partition.fstype))
                    self.disk_table.setItem(row, 3, QTableWidgetItem(f"{usage.total/(1024**3):.2f} GB"))
                    self.disk_table.setItem(row, 4, QTableWidgetItem(f"{usage.used/(1024**3):.2f} GB"))
                    self.disk_table.setItem(row, 5, QTableWidgetItem(f"{usage.free/(1024**3):.2f} GB"))
                    
                except PermissionError:
                    continue
                    
        except Exception as e:
            print(f"Disk info error: {e}")
            
    def update_process_table(self, processes):
        """Update process table"""
        try:
            selected_pids = set()
            for item in self.process_table.selectedItems():
                if item.column() == 0:
                    selected_pids.add(int(item.text()))
            
            self.process_table.setSortingEnabled(False)
            self.process_table.setRowCount(len(processes))
            
            for row, proc in enumerate(processes):
                # PID
                pid_item = QTableWidgetItem(str(proc['pid']))
                pid_item.setTextAlignment(Qt.AlignCenter)
                self.process_table.setItem(row, 0, pid_item)
                
                # Name
                name_item = QTableWidgetItem(proc['name'] or 'N/A')
                self.process_table.setItem(row, 1, name_item)
                
                # CPU %
                cpu_item = QTableWidgetItem(f"{proc['cpu_percent']:.1f}")
                cpu_item.setTextAlignment(Qt.AlignCenter)
                if proc['cpu_percent'] > 50:
                    cpu_item.setForeground(QColor(70, 130, 180))
                self.process_table.setItem(row, 2, cpu_item)
                
                # Memory %
                mem_item = QTableWidgetItem(f"{proc['memory_percent']:.1f}")
                mem_item.setTextAlignment(Qt.AlignCenter)
                if proc['memory_percent'] > 10:
                    mem_item.setForeground(QColor(30, 144, 255))
                self.process_table.setItem(row, 3, mem_item)
                
                # Status
                status_item = QTableWidgetItem(proc['status'])
                status_item.setTextAlignment(Qt.AlignCenter)
                self.process_table.setItem(row, 4, status_item)
                
                # Threads
                threads_item = QTableWidgetItem(str(proc.get('num_threads', 'N/A')))
                threads_item.setTextAlignment(Qt.AlignCenter)
                self.process_table.setItem(row, 5, threads_item)
                
                # User
                user_item = QTableWidgetItem(proc.get('username', 'N/A'))
                self.process_table.setItem(row, 6, user_item)
                
                # Uptime
                uptime_item = QTableWidgetItem(proc.get('uptime', 'N/A'))
                uptime_item.setTextAlignment(Qt.AlignCenter)
                self.process_table.setItem(row, 7, uptime_item)
                
                if proc['pid'] in selected_pids:
                    self.process_table.selectRow(row)
            
            self.process_table.setSortingEnabled(True)
            
        except Exception as e:
            print(f"Process table error: {e}")
            
    def filter_processes(self, text):
        """Filter process table"""
        for row in range(self.process_table.rowCount()):
            show = False
            for col in range(self.process_table.columnCount()):
                item = self.process_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.process_table.setRowHidden(row, not show)
            
    def request_process_refresh(self):
        """Request process refresh"""
        pass
        
    def kill_selected_process(self):
        """Kill selected process"""
        selected = self.process_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "No process selected")
            return
            
        pid_item = self.process_table.item(selected[0].row(), 0)
        pid = int(pid_item.text())
        name_item = self.process_table.item(selected[0].row(), 1)
        name = name_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm",
            f"End process '{name}' (PID: {pid})?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                QMessageBox.information(self, "Success", f"Process {pid} terminated")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
                
    def export_data(self):
        """Export historical data"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "system_monitor_export.csv", "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with self.db_lock:
                    self.cursor.execute("SELECT * FROM system_logs ORDER BY timestamp")
                    rows = self.cursor.fetchall()
                    
                with open(filename, 'w') as f:
                    f.write("Timestamp,CPU %,Memory %,Memory Used,Disk %,Network Sent,Network Recv\n")
                    for row in rows:
                        f.write(','.join(map(str, row)) + '\n')
                        
                QMessageBox.information(self, "Success", f"Exported {len(rows)} records")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def clear_history(self):
        """Clear historical data"""
        reply = QMessageBox.question(
            self, "Confirm",
            "Clear all historical data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with self.db_lock:
                    self.cursor.execute("DELETE FROM system_logs")
                    self.conn.commit()
                QMessageBox.information(self, "Success", "History cleared")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def show_settings(self):
        """Show settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        refresh_spin = QSpinBox()
        refresh_spin.setRange(500, 5000)
        refresh_spin.setSingleStep(100)
        refresh_spin.setValue(self.refresh_rate)
        refresh_spin.setSuffix(" ms")
        layout.addRow("Refresh Rate:", refresh_spin)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_rate = refresh_spin.value()
            self.timer.setInterval(self.refresh_rate)
            self.save_settings()
            
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>System Monitor Pro</h2>
        <p><b>Glassmorphism Edition</b></p>
        <p>Version 3.5 - Enhanced</p>
        <br>
        <p>Professional system monitoring with stunning glassmorphism design</p>
        <p>Light blue and white color scheme</p>
        <br>
        <p><b>New Features:</b></p>
        <ul>
        <li>🔔 Configurable system alerts</li>
        <li>📈 Performance history tracking</li>
        <li>🔋 Battery monitoring</li>
        <li>📊 Detailed statistics</li>
        <li>⚡ Real-time notifications</li>
        </ul>
        <br>
        <p>Built with PyQt5 and psutil</p>
        """
        
        QMessageBox.about(self, "About", about_text)
    
    def check_alerts(self):
        """Check and update alert configurations"""
        try:
            # Update alert manager with current settings
            for key, widgets in self.alert_widgets.items():
                enabled = widgets['enable'].isChecked()
                threshold = widgets['slider'].value()
                self.alert_manager.toggle_alert(key, enabled)
                self.alert_manager.set_threshold(key, threshold)
            
            # Check for alerts
            self.alert_manager.check_alerts()
        except Exception as e:
            print(f"Alert check error: {e}")
    
    def handle_alert(self, title, message, severity):
        """Handle triggered alert"""
        try:
            # Log to alert log
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {title}: {message}\n"
            self.alert_log.append(log_entry)
            
            # Show system tray notification
            icon = QSystemTrayIcon.Critical if severity == "critical" else QSystemTrayIcon.Warning
            
            # Create tray icon if it doesn't exist
            if not hasattr(self, 'tray_icon'):
                self.tray_icon = QSystemTrayIcon(self)
                self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            
            self.tray_icon.show()
            self.tray_icon.showMessage(title, message, icon, 5000)
            
        except Exception as e:
            print(f"Alert handler error: {e}")
    
    def test_alert(self):
        """Test the alert system"""
        self.handle_alert(
            "Test Alert",
            "This is a test notification from System Monitor Pro",
            "warning"
        )
        QMessageBox.information(
            self,
            "Alert Test",
            "Test alert sent! Check the alert log and system notifications."
        )
    
    def load_history_data(self, time_range):
        """Load performance history from database"""
        try:
            with self.db_lock:
                # Calculate time delta
                if time_range == "Last Hour":
                    delta = timedelta(hours=1)
                elif time_range == "Last 6 Hours":
                    delta = timedelta(hours=6)
                elif time_range == "Last 24 Hours":
                    delta = timedelta(days=1)
                else:  # Last Week
                    delta = timedelta(weeks=1)
                
                cutoff_time = (datetime.now() - delta).strftime("%Y-%m-%d %H:%M:%S")
                
                self.cursor.execute("""
                    SELECT * FROM system_logs 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                
                rows = self.cursor.fetchall()
                
                self.history_table.setSortingEnabled(False)
                self.history_table.setRowCount(len(rows))
                
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        if col_idx == 0:  # Timestamp
                            item = QTableWidgetItem(str(value))
                        elif col_idx in [1, 2, 4]:  # Percentages
                            item = QTableWidgetItem(f"{float(value):.1f}")
                            item.setTextAlignment(Qt.AlignCenter)
                        elif col_idx == 3:  # Memory in GB
                            item = QTableWidgetItem(f"{float(value) / (1024**3):.2f}")
                            item.setTextAlignment(Qt.AlignCenter)
                        else:  # Network in MB
                            item = QTableWidgetItem(f"{float(value) / (1024**2):.2f}")
                            item.setTextAlignment(Qt.AlignCenter)
                        
                        self.history_table.setItem(row_idx, col_idx, item)
                
                self.history_table.setSortingEnabled(True)
                
        except Exception as e:
            print(f"History load error: {e}")
    
    def show_statistics(self):
        """Show performance statistics dialog"""
        try:
            with self.db_lock:
                self.cursor.execute("""
                    SELECT 
                        AVG(cpu_percent), MAX(cpu_percent), MIN(cpu_percent),
                        AVG(memory_percent), MAX(memory_percent), MIN(memory_percent),
                        AVG(disk_percent), MAX(disk_percent), MIN(disk_percent)
                    FROM system_logs
                """)
                stats = self.cursor.fetchone()
            
            if stats and stats[0] is not None:
                dialog = QDialog(self)
                dialog.setWindowTitle("Performance Statistics")
                dialog.setMinimumWidth(500)
                
                layout = QVBoxLayout(dialog)
                
                # Create statistics display
                stats_text = f"""
                <h3 style="color: #1E90FF;">System Performance Statistics</h3>
                
                <h4 style="color: #4682B4;">🖥️ CPU</h4>
                <p>Average: {stats[0]:.2f}% | Peak: {stats[1]:.2f}% | Lowest: {stats[2]:.2f}%</p>
                
                <h4 style="color: #4682B4;">💾 Memory</h4>
                <p>Average: {stats[3]:.2f}% | Peak: {stats[4]:.2f}% | Lowest: {stats[5]:.2f}%</p>
                
                <h4 style="color: #4682B4;">💿 Disk</h4>
                <p>Average: {stats[6]:.2f}% | Peak: {stats[7]:.2f}% | Lowest: {stats[8]:.2f}%</p>
                """
                
                text_label = QLabel(stats_text)
                text_label.setWordWrap(True)
                text_label.setStyleSheet("padding: 20px;")
                layout.addWidget(text_label)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec_()
            else:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No historical data available yet. Keep the monitor running to collect data."
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load statistics: {str(e)}")
    
    def open_task_manager(self):
        """Open system task manager"""
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['taskmgr'])
            elif platform.system() == 'Linux':
                subprocess.Popen(['gnome-system-monitor'])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Activity Monitor'])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open task manager: {str(e)}")
    
    def open_resource_monitor(self):
        """Open resource monitor"""
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['perfmon', '/res'])
            else:
                QMessageBox.information(self, "Info", "Resource Monitor is Windows-specific")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open resource monitor: {str(e)}")
    
    def open_cmd(self):
        """Open command prompt"""
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['cmd'])
            else:
                subprocess.Popen(['xterm'])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open command prompt: {str(e)}")
    
    def open_powershell(self):
        """Open PowerShell"""
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['powershell'])
            else:
                QMessageBox.information(self, "Info", "PowerShell opening is Windows-specific")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open PowerShell: {str(e)}")
    
    def take_screenshot(self):
        """Take a screenshot of the application"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_monitor_screenshot_{timestamp}.png"
            
            # Take screenshot
            pixmap = self.grab()
            pixmap.save(filename, "PNG")
            
            QMessageBox.information(
                self,
                "Screenshot Saved",
                f"Screenshot saved as:\n{filename}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to take screenshot: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>System Monitor Pro</h2>
        <p><b>Glassmorphism Edition</b></p>
        <p>Version 3.5 - Enhanced</p>
        <br>
        <p>Professional system monitoring with stunning glassmorphism design</p>
        <p>Light blue and white color scheme</p>
        <br>
        <p><b>New Features:</b></p>
        <ul>
        <li>🔔 Configurable system alerts</li>
        <li>📈 Performance history tracking</li>
        <li>🔋 Battery monitoring</li>
        <li>📊 Detailed statistics</li>
        <li>⚡ Real-time notifications</li>
        <li>🚀 Quick actions menu</li>
        </ul>
        <br>
        <p>Built with PyQt5 and psutil</p>
        """
        
        QMessageBox.about(self, "About", about_text)
        
    def closeEvent(self, event):
        """Handle close event"""
        try:
            self.process_worker.stop()
            self.network_worker.stop()
        except:
            pass
            
        self.save_settings()
        
        try:
            with self.db_lock:
                self.conn.close()
        except:
            pass
            
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("System Monitor Pro - Glass")
    
    window = SystemMonitorGlass()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()