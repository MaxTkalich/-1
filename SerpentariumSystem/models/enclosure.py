class Enclosure:
    def __init__(
        self,
        code,
        zone,
        temperature,
        humidity,
        has_water,
        lighting_mode,
        capacity,
        notes=""
    ):
        self.code = code
        self.zone = zone
        self.temperature = temperature
        self.humidity = humidity
        self.has_water = has_water
        self.lighting_mode = lighting_mode
        self.capacity = capacity
        self.notes = notes