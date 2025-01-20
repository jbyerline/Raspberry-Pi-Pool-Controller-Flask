class WaterfallController:
    def __init__(self, hardware):
        self.hardware = hardware
        self.arduino_pin = 3  # Adjust based on wiring
        self.status = "off"

    def toggle(self, action):
        if action in ["on", "off"]:
            self.status = action
            self.hardware.control_arduino_relay(self.arduino_pin, action)
            print(f"Waterfall {action}")

    def get_status(self):
        return self.status
