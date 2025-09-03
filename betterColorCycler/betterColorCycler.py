from krita import *
from math import gcd
import math
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QTimer


max_steps = 60
angle_rel = 15

start_pos = 12
sensitivity = 1
sensitivity_fine = 4
sv_step_size = 256 / 30  # ~8.533
sv_num_steps = 30
show_mesg = True

class BetterColorCycler(krita.Extension):

    # def __init__(self, parent):
    #     super(BetterColorCycler, self).__init__(parent)
    #
    #     appNotifier  = Application.notifier()
    #     appNotifier.windowCreated.connect(self.loadActions)

    # def __init__(self, parent):
    #     super(BetterColorCycler, self).__init__(parent)
    #     appNotifier = Application.notifier()
    #     appNotifier.windowCreated.connect(self.loadActions)
    #     appNotifier.activeViewChanged.connect(lambda *_: self.attach_view_notifier())
    def __init__(self, parent):
        super(BetterColorCycler, self).__init__(parent)

        # ---- Core state (safe defaults so signals won't break things) ----
        self.prev_col = None

        # Hue tracking
        self.abs_step = 0
        self.abs_step_before_fine = 0
        self.tog_fine = False
        self.h = 0.0
        self.h_anchor = 0.0

        # SV tracking
        self.sv = [0, 0]
        self.sv_step = [0, 0]
        self.sv_new_step = [0, 0]
        self.sv_deltas = [0, 0]
        self.sv_prev_mode = None

        # Settings-dependent values (set later in setup)
        self.max_steps = 0
        self.sat_num_steps = 0
        self.val_num_steps = 0
        self.sat_step_size = 0.0
        self.val_step_size = 0.0
        self.rel_max_steps = 0
        self.rel_revs = 0

        # Hook Krita notifiers
        appNotifier = Application.notifier()
        appNotifier.windowCreated.connect(self.loadActions)
        # appNotifier.activeViewChanged.connect(lambda *_: self.attach_view_notifier())
        # appNotifier.windowCreated.connect(lambda _: self.attach_view_notifier())
        appNotifier.windowCreated.connect(self.attach_view_notifier)




    def updateConfiguration(self, newHueSteps, newSatSteps, newValSteps):
        from PyQt5.QtCore import QSettings
        settings = QSettings()

        # Update instance variables.
        self.max_steps = newHueSteps
        self.sat_num_steps = newSatSteps
        self.val_num_steps = newValSteps
        self.sat_step_size = 255.0 / self.sat_num_steps
        self.val_step_size = 255.0 / self.val_num_steps

        # Write new values to QSettings.
        settings.setValue("BetterColorCycler/hue_steps", newHueSteps)
        settings.setValue("BetterColorCycler/sat_steps", newSatSteps)
        settings.setValue("BetterColorCycler/val_steps", newValSteps)

        self.toast(f"Configuration updated: Hue Steps = {newHueSteps}, Sat Steps = {newSatSteps}, Value Steps = {newValSteps}")

    # def setup(self):
    #     from PyQt5.QtCore import QSettings
    #     settings = QSettings()
    #     # Read values from settings (or use default globals if not set)
    #     self.max_steps = settings.value("BetterColorCycler/hue_steps", max_steps, type=int)
    #     self.sat_num_steps = settings.value("BetterColorCycler/sat_steps", 30, type=int)
    #     self.val_num_steps = settings.value("BetterColorCycler/val_steps", 30, type=int)
    #
    #     # Compute step sizes based on the number of steps.
    #     self.sat_step_size = 255.0 / self.sat_num_steps
    #     self.val_step_size = 255.0 / self.val_num_steps
    #
    #     # Initialize state
    #     self.abs_step = 0
    #     self.abs_step_before_fine = 0
    #     self.prev_col = None
    #     self.tog_fine = False
    #     self.h = 0
    #     self.h_anchor = 0.0
    #
    #     # Relative hue stepping setup
    #     self.rel_max_steps = self.lcm(angle_rel, 360) / angle_rel
    #     self.rel_revs = self.lcm(angle_rel, 360) / 360
    #
    #     # SV-related state
    #     self.sv = [0, 0]
    #     self.sv_step = [0, 0]
    #     self.sv_new_step = [0, 0]
    #     self.sv_deltas = [0, 0]
    #     self.sv_prev_mode = None
    #
    #     self.attach_view_notifier()
    def setup(self):
        """Load settings + compute step sizes."""
        from PyQt5.QtCore import QSettings
        settings = QSettings()

        # Load settings
        self.max_steps = settings.value("BetterColorCycler/hue_steps", max_steps, type=int)
        self.sat_num_steps = settings.value("BetterColorCycler/sat_steps", 30, type=int)
        self.val_num_steps = settings.value("BetterColorCycler/val_steps", 30, type=int)

        # Step sizes
        self.sat_step_size = 255.0 / self.sat_num_steps
        self.val_step_size = 255.0 / self.val_num_steps

        # Relative hue stepping setup
        self.rel_max_steps = self.lcm(angle_rel, 360) / angle_rel
        self.rel_revs = self.lcm(angle_rel, 360) / 360

        # Attach notifier to active view
        self.attach_view_notifier()


    # def attach_view_notifier(self):
    #     win = Application.activeWindow()
    #     if not win:
    #         return
    #     view = win.activeView()
    #     if not view:
    #         return
    #     try:
    #         view.notifier().foregroundColorChanged.disconnect(self.onExternalColorChange)
    #     except Exception:
    #         pass
    #     view.notifier().foregroundColorChanged.connect(self.onExternalColorChange)
    #     # # Attach notifier to track external color changes
    #     # window = Application.activeWindow()
    #     # if window and window.activeView():
    #     #     view = window.activeView()
    #     #     view.notifier().foregroundColorChanged.connect(self.onExternalColorChange)
    # def attach_view_notifier(self):
    #     """Attach color-change notifier to the active view."""
    #     win = Application.activeWindow()
    #     if not win:
    #         return
    #     view = win.activeView()
    #     if not view:
    #         return
    #
    #     # Avoid duplicate connections
    #     try:
    #         view.notifier().foregroundColorChanged.disconnect(self.onExternalColorChange)
    #     except Exception:
    #         pass
    #     view.notifier().foregroundColorChanged.connect(self.onExternalColorChange)
    def attach_view_notifier(self, retries=3):
        win = Application.activeWindow()
        if not win:
            return
        view = win.activeView()
        if not view:
            return

        notifier = getattr(view, "notifier", None)
        if notifier is None:
            # Retry a few times with slight delay in case the view isn't fully initialized
            if retries > 0:
                QTimer.singleShot(100, lambda: self.attach_view_notifier(retries - 1))
            return

        try:
            notifier().foregroundColorChanged.disconnect(self.onExternalColorChange)
        except Exception:
            pass
        notifier().foregroundColorChanged.connect(self.onExternalColorChange)



    # def resetAllSV(self, col):
    #     """Reset both saturation and value step counters to match the given color."""
    #     self.sv_prev_mode = None
    #     self.sv = [col.hsvSaturation(), col.value()]
    #     self.sv_new_step = [
    #         math.ceil(self.sv[0] / self.sat_step_size),
    #         math.ceil(self.sv[1] / self.val_step_size)
    #     ]
    #     self.sv_step = self.sv_new_step.copy()
    def resetAllSV(self, col):
        """Reset both saturation and value step counters to match the given color."""
        # Safety: ensure setup was run
        if self.sat_step_size == 0 or self.val_step_size == 0:
            self.setup()

        self.sv_prev_mode = None
        self.sv = [col.hsvSaturation(), col.value()]
        self.sv_new_step = [
            math.ceil(self.sv[0] / self.sat_step_size),
            math.ceil(self.sv[1] / self.val_step_size)
        ]
        self.sv_step = self.sv_new_step.copy()



    def onExternalColorChange(self):
        """Called whenever Krita's foreground color changes externally (picker, palette, etc.)."""
        col = self.getCurFGColor()
        self.resyncFromColor(col)
        # self.toast(f"Synced to external color {col.name()}")


    # def resyncFromColor(self, col):
    #     """Reset all plugin state from the given QColor."""
    #     # Reset hue tracking
    #     self.h = col.hsvHueF()
    #     self.h_anchor = self.h    # <--- anchor current hue
    #     self.abs_step = 0
    #     self.abs_step_before_fine = 0
    #
    #     # Reset SV tracking
    #     self.sv_prev_mode = None
    #     self.sv = [col.hsvSaturation(), col.value()]
    #     self.sv_new_step = [
    #         math.ceil(self.sv[0] / self.sat_step_size),
    #         math.ceil(self.sv[1] / self.val_step_size)
    #     ]
    #     self.sv_step = self.sv_new_step.copy()
    #
    #     # Remember this color
    #     self.prev_col = col
    def resyncFromColor(self, col):
        """Reset all plugin state from the given QColor."""

        # Safety: ensure setup was run
        if self.sat_step_size == 0 or self.val_step_size == 0:
            self.setup()

        # Reset hue tracking
        self.h = col.hsvHueF()
        self.h_anchor = self.h
        self.abs_step = 0
        self.abs_step_before_fine = 0

        # Reset SV tracking
        self.sv_prev_mode = None
        self.sv = [col.hsvSaturation(), col.value()]
        self.sv_new_step = [
            math.ceil(self.sv[0] / self.sat_step_size),
            math.ceil(self.sv[1] / self.val_step_size)
        ]
        self.sv_step = self.sv_new_step.copy()

        # Remember this color
        self.prev_col = col



    def createActions(self, window):
        pass


    def loadActions(self):
        window = Application.activeWindow()

        # Create the top-level plugin menu and store it as an attribute.
        self.menu_bcc = QtWidgets.QMenu("BetterColorCycler", window.qwindow())

        # Create the parent action in the "tools/scripts" category and attach the QMenu.
        action_bcc = window.createAction("better_color_cycler_menu", "BetterColorCycler", "tools/scripts")
        action_bcc.setMenu(self.menu_bcc)

        # Helper function: create an action in the submenu.
        def add_plugin_action(name, label, callback):
            a = window.createAction(name, label, "tools/scripts/better_color_cycler_menu")
            a.triggered.connect(callback)
            self.menu_bcc.addAction(a)

        # Add all your sub-actions.
        add_plugin_action("rotate_c_rel", "Rotate Hue Clockwise (Relative)", lambda: self.makeStep(False, 1))
        add_plugin_action("rotate_cc_rel", "Rotate Hue Counter-Clockwise (Relative)", lambda: self.makeStep(False, -1))
        add_plugin_action("rotate_c_abs", "Rotate Hue Clockwise (Absolute)", lambda: self.makeStep(True, 1))
        add_plugin_action("rotate_cc_abs", "Rotate Hue Counter-Clockwise (Absolute)", lambda: self.makeStep(True, -1))
        add_plugin_action("reset_step_counter", "Reset Step Counter", self.resetSteps)
        add_plugin_action("toggle_fine", "Toggle Fine Steps", self.toggleFine)
        add_plugin_action("shift_s_pos", "Increase Saturation", lambda: self.shiftSV(0, 1))
        add_plugin_action("shift_s_neg", "Decrease Saturation", lambda: self.shiftSV(0, -1))
        add_plugin_action("shift_v_pos", "Increase Value", lambda: self.shiftSV(1, 1))
        add_plugin_action("shift_v_neg", "Decrease Value", lambda: self.shiftSV(1, -1))
        add_plugin_action("bcs_configure", "Configure BetterColorCycler", self.showSettingsDialog)


    def testColorChanged(self,col):         # color must have changed outside this script
        return self.prev_col == None or self.prev_col.name() != col.name()


    def testSVModeChanged(self,mod):
        return self.sv_prev_mode == None or self.sv_prev_mode != mod


    def resetRelMode(self,col):
        self.prev_col = col
        self.updateHue(col.hsvHueF(),col.hsvSaturationF())


    # def resetSV(self, col, mod):
    #     """
    #     Resets the internal step counters for Saturation and Value
    #     based on the current foreground color.
    #     """
    #     self.sv_prev_mode = mod
    #     self.updateHue(col.hsvHueF(), col.hsvSaturationF())
    #
    #     # Capture the current saturation and value (range 0–255)
    #     self.sv = [col.hsvSaturation(), col.value()]
    #
    #     # Safeguard: if the number of steps is not defined, set a default (30 steps)
    #     if not hasattr(self, 'sat_num_steps'):
    #         self.sat_num_steps = 30
    #     if not hasattr(self, 'val_num_steps'):
    #         self.val_num_steps = 30
    #
    #     # Safeguard: if the step sizes are not defined, compute them from the number of steps
    #     if not hasattr(self, 'sat_step_size'):
    #         self.sat_step_size = 255.0 / self.sat_num_steps
    #     if not hasattr(self, 'val_step_size'):
    #         self.val_step_size = 255.0 / self.val_num_steps
    #
    #     # Determine the starting step value for each channel
    #     self.sv_new_step = [
    #         math.ceil(self.sv[0] / self.sat_step_size),
    #         math.ceil(self.sv[1] / self.val_step_size)
    #     ]
    #     self.sv_step = self.sv_new_step.copy()
    def resetSV(self, col, mod):
        """Resets the internal step counters for Saturation and Value."""
        self.sv_prev_mode = mod
        self.updateHue(col.hsvHueF(), col.hsvSaturationF())

        self.sv = [col.hsvSaturation(), col.value()]

        # Ensure safe defaults
        if not hasattr(self, 'sat_num_steps') or self.sat_num_steps <= 0:
            self.sat_num_steps = 30
        if not hasattr(self, 'val_num_steps') or self.val_num_steps <= 0:
            self.val_num_steps = 30

        if not hasattr(self, 'sat_step_size') or self.sat_step_size <= 0:
            self.sat_step_size = 255.0 / self.sat_num_steps
        if not hasattr(self, 'val_step_size') or self.val_step_size <= 0:
            self.val_step_size = 255.0 / self.val_num_steps

        self.sv_new_step = [
            math.ceil(self.sv[0] / self.sat_step_size),
            math.ceil(self.sv[1] / self.val_step_size)
        ]
        self.sv_step = self.sv_new_step.copy()



    def resetSteps(self):
        self.abs_step = 0
        if (show_mesg):
            self.toast("Step counter has been reset.")

    # def makeStep(self, mode_abs, direction):
    #     col = self.getCurFGColor()
    #
    #     if mode_abs:
    #         self.abs_step += direction
    #         sensitivity_used = sensitivity_fine if self.tog_fine else sensitivity
    #
    #         # fraction of full circle for current step
    #         step_fraction = (self.abs_step % (self.max_steps * sensitivity_used)) / (self.max_steps * sensitivity_used)
    #
    #         # absolute hue is anchored at last picked color
    #         new_hue = (self.h_anchor + step_fraction) % 1.0
    #         newcol = QColor.fromHsvF(new_hue, col.hsvSaturationF(), col.valueF())
    #
    #         self.setNewFGColor(newcol)
    #         self.resetRelMode(newcol)
    #
    #     else:
    #         if self.testColorChanged(col):
    #             self.resyncFromColor(col)
    #
    #         deg = ((direction % (self.rel_max_steps * self.getSensitivity())) / (self.rel_max_steps * self.getSensitivity())) * self.rel_revs
    #         self.setNewFGColor(self.rotateHue(deg, col, self.h))
    #         self.resetRelMode(col)


    def makeStep(self, mode_abs, direction):
        # Safety: ensure setup was run
        if self.sat_step_size == 0 or self.val_step_size == 0:
            self.setup()
        col = self.getCurFGColor()

        # Always resync if the color changed outside the plugin (picker, palette, etc.)
        if self.testColorChanged(col):
            self.resyncFromColor(col)
            col = self.prev_col  # after resync, keep using the synced color

        if mode_abs:
            self.abs_step += direction
            sensitivity_used = sensitivity_fine if self.tog_fine else sensitivity

            # fraction of full circle for current step
            step_fraction = (self.abs_step % (self.max_steps * sensitivity_used)) / (self.max_steps * sensitivity_used)

            # absolute hue is anchored at last picked color
            new_hue = (self.h_anchor + step_fraction) % 1.0
            newcol = QColor.fromHsvF(new_hue, col.hsvSaturationF(), col.valueF())

            self.setNewFGColor(newcol)
            # don't change h_anchor here; it's supposed to remain the pick anchor
            self.resetRelMode(newcol)

        else:
            deg = ((direction % (self.rel_max_steps * self.getSensitivity())) /
                (self.rel_max_steps * self.getSensitivity())) * self.rel_revs
            self.setNewFGColor(self.rotateHue(deg, col, self.h))
            self.resetRelMode(col)


    def rotateHue(self,ix,col,h):        # 0...max_steps-1, starting at the top (start_pos)
        sv = [col.hsvSaturationF(),col.valueF()]
        self.updateHue((ix + h) % 1.0,col.hsvSaturationF())
        return QColor.fromHsvF(self.h,*sv)


    def shiftSV(self, mode_sv, direction):
        col = self.getCurFGColor()

        # Safeguard: if the saturation/value configuration isn't defined, initialize them with defaults.
        if not hasattr(self, 'sat_num_steps'):
            self.sat_num_steps = 30    # Default number of saturation steps.
        if not hasattr(self, 'val_num_steps'):
            self.val_num_steps = 30    # Default number of value steps.
        if not hasattr(self, 'sat_step_size'):
            self.sat_step_size = 255.0 / self.sat_num_steps
        if not hasattr(self, 'val_step_size'):
            self.val_step_size = 255.0 / self.val_num_steps
        if not hasattr(self, 'sv_step'):
            self.sv_step = [0, 0]
        if not hasattr(self, 'sv_new_step'):
            self.sv_new_step = [0, 0]

        # Only reset the SV step counters if the saturation/value mode has changed.
        if self.testSVModeChanged(mode_sv):
            self.resetSV(col, mode_sv)

        # Optionally update relative mode if an external color change is detected.
        if self.testColorChanged(col):
            self.resyncFromColor(col)

        # Determine the maximum number of steps for the selected channel.
        max_steps_channel = self.sat_num_steps if mode_sv == 0 else self.val_num_steps

        # Increment the step counter for the given channel and clamp it.
        self.sv_step[mode_sv] += direction
        self.sv_step[mode_sv] = self.between(self.sv_step[mode_sv], 0, max_steps_channel)

        # Calculate new saturation and value from the step counters.
        new_sat = int(round(self.between(self.sv_step[0] * self.sat_step_size, 0, 255)))
        new_val = int(round(self.between(self.sv_step[1] * self.val_step_size, 0, 255)))

        # Update the foreground color using the current hue, new saturation, and new value.
        self.setNewFGColor(QColor.fromHsv(int(self.h * 360), new_sat, new_val))


    def setNewFGColor(self,col):
        view = Application.activeWindow().activeView()
        view.setForeGroundColor(ManagedColor.fromQColor(col))
        self.prev_col = col
        return col


    def getCurFGColor(self):
        view = Application.activeWindow().activeView()
        return view.foregroundColor().colorForCanvas(None)


    def updateHue(self,h,s):      # prevent -1 hue when going 0 saturation or brightness
        if (s > 0):
            self.h = max(h,0)


    def getStartPos(self):      # start_pos is hour hand on a clock. def= 12 o'clock
        return (start_pos % 12) / 12 + 0.25


    def getSensitivity(self):
        return sensitivity_fine if (self.tog_fine) else sensitivity


    def toggleFine(self):
        self.resetRelMode(self.getCurFGColor())
        if (self.tog_fine):
            self.abs_step = self.abs_step_before_fine + self.abs_step - self.abs_step_before_fine * (sensitivity_fine / sensitivity)
            self.abs_step_before_fine = 0
        else:
            self.abs_step_before_fine = self.abs_step
            self.abs_step = self.abs_step_before_fine * (sensitivity_fine / sensitivity)
        self.tog_fine = not self.tog_fine
        if (show_mesg):
            self.toast(f"Fine mode is now toggled [{'on' if (self.tog_fine) else 'off'}]")


    def toast(self,msg):
        Application.activeWindow().activeView().showFloatingMessage(msg, QIcon(), 300, 1)
        print(f"[BetterColorCycler] {msg}")


    def lcm(self,a,b):
        return abs(a*b) // gcd(a,b)


    def between(self, n, lower, upper):
        return max(lower, min(n, upper))


    def showSettingsDialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton
        from PyQt5.QtCore import QSettings

        dialog = QDialog()
        dialog.setWindowTitle("BetterColorCycler Settings")
        layout = QVBoxLayout(dialog)

        # Create spin boxes for each configuration parameter.
        hue_spin = QSpinBox()
        hue_spin.setRange(1, 360)
        hue_spin.setValue(self.max_steps)  # current value if available
        layout.addLayout(self.createRow("Hue Steps:", hue_spin))

        sat_spin = QSpinBox()
        sat_spin.setRange(1, 255)
        sat_spin.setValue(self.sat_num_steps if hasattr(self, 'sat_num_steps') else 30)
        layout.addLayout(self.createRow("Saturation Steps:", sat_spin))

        val_spin = QSpinBox()
        val_spin.setRange(1, 255)
        val_spin.setValue(self.val_num_steps if hasattr(self, 'val_num_steps') else 30)
        layout.addLayout(self.createRow("Value Steps:", val_spin))

        apply_btn = QPushButton("Apply Settings")
        layout.addWidget(apply_btn)

        # Get QSettings instance.
        settings = QSettings()

        # This is where you put your code:
        apply_btn.clicked.connect(lambda: (
            settings.setValue("BetterColorCycler/hue_steps", hue_spin.value()),
            settings.setValue("BetterColorCycler/sat_steps", sat_spin.value()),
            settings.setValue("BetterColorCycler/val_steps", val_spin.value()),
            setattr(self, "max_steps", hue_spin.value()),
            setattr(self, "sat_num_steps", sat_spin.value()),
            setattr(self, "val_num_steps", val_spin.value()),
            setattr(self, "sat_step_size", 255.0 / sat_spin.value()),  # Adjust according to saturation steps
            setattr(self, "val_step_size", 255.0 / val_spin.value()),
            self.toast("Settings applied. They will persist across restarts."),
            dialog.accept()
        ))

        dialog.exec_()


    def createRow(label_text, current_value):
        label = QLabel(label_text)
        spin = QSpinBox()
        spin.setRange(1, 360)
        spin.setValue(current_value)
        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(spin)
        return spin, row

        settings = QSettings()

        hue_steps = settings.value("BetterColorCycler/hue_steps", max_steps, type=int)
        sv_steps = settings.value("BetterColorCycler/sv_steps", 30, type=int)

        hue_spin, row1 = createRow("Hue Steps", hue_steps)
        sat_spin, row2 = createRow("Saturation Steps", sv_steps)
        val_spin, row3 = createRow("Value Steps", sv_steps)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: (
            settings.setValue("BetterColorCycler/hue_steps", hue_spin.value()),
            settings.setValue("BetterColorCycler/sv_steps", sat_spin.value()),
            setattr(self, "max_steps", hue_spin.value()),
            setattr(self, "sv_num_steps", val_spin.value()),
            setattr(self, "sv_step_size", 256 / val_spin.value()),
            self.toast("Settings applied. Restart Krita for full effect."),
            dialog.accept()
        ))

        layout.addWidget(apply_btn)
        dialog.setLayout(layout)
        dialog.exec_()


    def updateHueSettings(self, newHueSteps):
        # Update your internal variable for hue steps.
        self.max_steps = newHueSteps
        self.toast(f"Hue steps updated to {newHueSteps}")
