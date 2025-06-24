from .betterColorCycler import BetterColorCycler
from .betterColorCyclerDocker import BetterColorCyclerDocker
from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase

# Register your extension.
Krita.instance().addExtension(BetterColorCycler(Krita.instance()))

# Create a dock widget factory.
# Note: The order here is:
#   (internal ID, dock position, widget class)
dockFactory = DockWidgetFactory(
    "betterColorCyclerDocker",            # Unique internal ID.
    DockWidgetFactoryBase.DockRight,      # Preferred dock area.
    BetterColorCyclerDocker               # The docker class.
)

# Register the dock widget factory with Krita.
Krita.instance().addDockWidgetFactory(dockFactory)
