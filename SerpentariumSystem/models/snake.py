class Snake:
    def __init__(
        self,
        nickname,
        species_id,
        age_years,
        sex,
        health_status,
        enclosure_id,
        last_feeding_date,
        notes=""
    ):
        self.nickname = nickname
        self.species_id = species_id
        self.age_years = age_years
        self.sex = sex
        self.health_status = health_status
        self.enclosure_id = enclosure_id
        self.last_feeding_date = last_feeding_date
        self.notes = notes