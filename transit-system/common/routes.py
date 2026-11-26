# Simulated bus routes, shared by every service.


ROUTES = {
    "R1": {
        "name": "Simcoe North",
        "stops": [
            ("S1", "Oshawa Centre", 43.8885, -78.8822),
            ("S2", "Downtown Oshawa", 43.8975, -78.8658),
            ("S3", "Simcoe & Rossland", 43.9150, -78.8680),
            ("S4", "Ontario Tech / Durham College", 43.9445, -78.8964),
        ],
    },
    "R2": {
        "name": "King Street East-West",
        "stops": [
            ("S5", "Whitby GO", 43.8655, -78.9380),
            ("S1", "Oshawa Centre", 43.8885, -78.8822),
            ("S2", "Downtown Oshawa", 43.8975, -78.8658),
            ("S6", "Harmony Terminal", 43.9030, -78.8330),
        ],
    },
    "R3": {
        "name": "Taunton Crosstown",
        "stops": [
            ("S7", "Taunton & Thickson", 43.9380, -78.9280),
            ("S4", "Ontario Tech / Durham College", 43.9445, -78.8964),
            ("S8", "Taunton & Harmony", 43.9420, -78.8460),
        ],
    },
}

VEHICLE_CAPACITY = 60   # max passengers per bus