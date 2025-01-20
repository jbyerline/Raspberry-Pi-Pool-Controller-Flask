class PoolPumpController:
    def __init__(self, hardware):
        self.hardware = hardware
        self.arduino_pin = 4  # Adjust based on wiring

    def toggle(self, action):
        if action in ["on", "off"]:
            self.hardware.control_arduino_relay(self.arduino_pin, action)
            print(f"Pool Pump {action}")
