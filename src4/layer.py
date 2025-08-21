class Layer:
    """Abstract base class for application layers."""
    def on_attach(self):
        """Called when the layer is added to the application."""
        pass

    def on_detach(self):
        """Called when the layer is removed from the application."""
        pass

    def on_update(self, time: float, frametime: float):
        """Called every frame for logic updates."""
        pass

    def on_imgui_render(self):
        """Called every frame for ImGui rendering."""
        pass

    def on_event(self, event_type: int, event_data: tuple):
        """Called when an event is published."""
        pass