from krita import DockWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QGroupBox
from PyQt5.QtCore import QSettings

class BetterColorCyclerDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("BetterColorCyclerDocker")
        self.setWindowTitle("Better Color Cycler Steps")

        # Create container and layout.
        container = QWidget()
        layout = QVBoxLayout(container)

        # Get persisted values.
        settings = QSettings()
        currentHue = settings.value("BetterColorCycler/hue_steps", 60, type=int)
        currentSat = settings.value("BetterColorCycler/sat_steps", 30, type=int)
        currentVal = settings.value("BetterColorCycler/val_steps", 30, type=int)

        # Create spin boxes using persisted values.
        self.spinHue = QSpinBox()
        self.spinHue.setRange(1, 360)
        self.spinHue.setValue(currentHue)

        self.spinSat = QSpinBox()
        self.spinSat.setRange(1, 255)
        self.spinSat.setValue(currentSat)

        self.spinVal = QSpinBox()
        self.spinVal.setRange(1, 255)
        self.spinVal.setValue(currentVal)

        # Add your configuration widgets into the layout.
        configLayout = QHBoxLayout()
        configLayout.addWidget(QLabel("Hue:"))
        configLayout.addWidget(self.spinHue)
        configLayout.addWidget(QLabel("Sat:"))
        configLayout.addWidget(self.spinSat)
        configLayout.addWidget(QLabel("Val:"))
        configLayout.addWidget(self.spinVal)
        layout.addLayout(configLayout)


        # Optional: Add an "Apply" button so the user can update the configuration.
        applyBtn = QPushButton("Apply Settings")
        applyBtn.clicked.connect(self.applyConfiguration)
        layout.addWidget(applyBtn)

        # (Add other parts of your Docker UI as needed...)

        self.setWidget(container)

    def applyConfiguration(self):
        newHueSteps = self.spinHue.value()
        newSatSteps = self.spinSat.value()
        newValSteps = self.spinVal.value()
        # Pass these values to your extension via a callback.
        self.callExtension(lambda ext: ext.updateConfiguration(newHueSteps, newSatSteps, newValSteps))

    def callExtension(self, callback):
        from krita import Krita
        for ext in Krita.instance().extensions():
            if ext.__class__.__name__ == "BetterColorCycler":
                callback(ext)
                break

    def canvasChanged(self, canvas):
        # Required override – no action needed for now.
        pass


