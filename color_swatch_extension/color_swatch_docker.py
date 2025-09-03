from krita import DockWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QImage
from PyQt5.QtCore import Qt

class ColorSwatchDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ColorSwatchDocker")
        self.setWindowTitle("Color Swatch")
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(2,2,2,2)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(40, 40)
        lay.addWidget(self.preview_label)
        self.setWidget(w)
        self.checker_img = self.create_checker_image()

    def update_display(self, color, eraser=False):
        """Update swatch: solid color or checkerboard if eraser is active."""
        size = self.preview_label.size()
        if size.width() <= 0 or size.height() <= 0:
            return

        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)

        if eraser:
            # Draw checkerboard for transparency
            checker_size = 6
            for y in range(0, size.height(), checker_size):
                for x in range(0, size.width(), checker_size):
                    if (x // checker_size + y // checker_size) % 2 == 0:
                        p.fillRect(x, y, checker_size, checker_size, QColor(200, 200, 200))
                    else:
                        p.fillRect(x, y, checker_size, checker_size, QColor(255, 255, 255))
        else:
            # Fill with the actual color
            p.fillRect(0, 0, size.width(), size.height(), color)

        p.end()
        self.preview_label.setPixmap(pm)

    def canvasChanged(self, canvas):
        pass


    def updateSwatch(self, qcolor, eraser=False):
        hex_color = qcolor.name()
        # print(f"ColorSwatchDocker: updateSwatch -> {hex_color}, eraser={eraser}")

        size = self.preview_label.size()
        if size.width() <= 0 or size.height() <= 0:
            return
        pm = QPixmap(size); pm.fill(Qt.transparent)

        p = QPainter(pm)
        if eraser:
            brush = QBrush(self.checker_img)
            p.fillRect(0, 0, size.width(), size.height(), brush)
        else:
            p.fillRect(0, 0, size.width(), size.height(), qcolor)
        p.end()

        self.preview_label.setPixmap(pm)


    def create_checker_image(self):
        img = QImage(16, 16, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.fillRect(0, 0, 8, 8, QColor(200, 200, 200))
        p.fillRect(8, 8, 8, 8, QColor(200, 200, 200))
        p.end()
        return img
