from krita import Extension, Krita
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QApplication

class _InputEventFilter(QObject):
    """Global input hook: on any real user input, ask extension to maybe refresh."""
    def __init__(self, on_any_input):
        super().__init__()
        self._on_any_input = on_any_input

    def eventFilter(self, obj, event):
        et = event.type()
        if et in (
            QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseMove,
            QEvent.KeyPress, QEvent.KeyRelease,
            QEvent.Wheel,
            QEvent.TabletPress, QEvent.TabletRelease, QEvent.TabletMove,
            QEvent.Shortcut, QEvent.ShortcutOverride,
            QEvent.FocusIn, QEvent.FocusOut,
            QEvent.DragEnter, QEvent.Drop, QEvent.HoverMove
        ):
            try:
                self._on_any_input()
            except Exception as e:
                # print("ColorSwatchExtension: event filter callback error:", e)
                pass
        return False  # never swallow events


class ColorSwatchExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self._event_filter = None
        self._last_color_name = None
        self._last_eraser = None
        self._eraser_mode = False

    def setup(self):
        # print("ColorSwatchExtension: setup()")
        Krita.instance().notifier().windowCreated.connect(self._attach_to_active_window)

    def createActions(self, window):
        # print("ColorSwatchExtension: createActions()")
        self._attach_to_active_window()

    # ---- internals ---------------------------------------------------------

    def _attach_to_active_window(self):
        app = Krita.instance()
        win = app.activeWindow()
        if not win:
            return

        if self._event_filter is None:
            self._event_filter = _InputEventFilter(self._maybe_update_from_fg)
            QApplication.instance().installEventFilter(self._event_filter)
            try:
                win.qwindow().installEventFilter(self._event_filter)
                # Also connect to erase toggle
                erase_action = Krita.instance().action("erase_action")
                if erase_action:
                    erase_action.toggled.connect(self._on_erase_toggled)

            except Exception:
                pass

        # Prime once so the docker shows the initial color
        self._maybe_update_from_fg()

    def _on_erase_toggled(self, state):
        self._eraser_mode = state
        # force refresh so docker updates immediately
        self._maybe_update_from_fg()


    def _maybe_update_from_fg(self):
        """Compare current FG color with last; if changed or eraser toggled, push to docker."""
        try:
            app = Krita.instance()
            win = app.activeWindow()
            if not win:
                return
            view = win.activeView()
            if not view:
                return

            qcol = view.foregroundColor()
            if qcol is None:
                return
            qcol = qcol.colorForCanvas(view.canvas())
            if not qcol:
                return

            # Get current tool safely
            try:
                tool_id = win.qwindow().activeTool()
            except Exception:
                tool_id = ""
            eraser = self._eraser_mode

            new_hex = qcol.name()

            if new_hex != self._last_color_name or eraser != self._last_eraser:
                self._last_color_name = new_hex
                self._last_eraser = eraser
                # print(f"ColorSwatchExtension: color changed -> {new_hex}, eraser={eraser}")

                for docker in app.dockers():
                    if docker.objectName() == "ColorSwatchDocker":
                        docker.updateSwatch(qcol, eraser)

        except Exception as e:
            # print("ColorSwatchExtension: _maybe_update_from_fg error:", e)
            pass

