class Configuration:
    def __init__(self, normalise_by_sbm):
        self.normalise_by_sbm: bool = normalise_by_sbm

        self.name = f"Normalised to sbm + {normalise_by_sbm}"




    def __repr__(self):
        return self.name
