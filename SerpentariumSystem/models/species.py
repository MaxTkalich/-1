class Species:
    def __init__(
        self,
        common_name,
        latin_name,
        family_name,
        is_venomous,
        min_temperature,
        max_temperature,
        humidity_min,
        humidity_max,
        water_requirement,
        food_type,
        feeding_interval_days,
        average_food_amount,
        notes=""
    ):
        self.common_name = common_name
        self.latin_name = latin_name
        self.family_name = family_name
        self.is_venomous = is_venomous
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.humidity_min = humidity_min
        self.humidity_max = humidity_max
        self.water_requirement = water_requirement
        self.food_type = food_type
        self.feeding_interval_days = feeding_interval_days
        self.average_food_amount = average_food_amount
        self.notes = notes