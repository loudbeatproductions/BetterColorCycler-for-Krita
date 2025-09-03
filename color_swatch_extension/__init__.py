from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from .color_swatch_extension import ColorSwatchExtension
from .color_swatch_docker import ColorSwatchDocker

# print(">>> ColorSwatchExtension: registering")

# Register the extension
Krita.instance().addExtension(ColorSwatchExtension(Krita.instance()))

# Register the docker
docker_factory = DockWidgetFactory(
    "ColorSwatchDocker",
    DockWidgetFactoryBase.DockRight,
    ColorSwatchDocker
)
Krita.instance().addDockWidgetFactory(docker_factory)
