class Configuration:
    def __init__(self, normalise_by_sbm, background_method):
        self.normalise_by_sbm: bool = normalise_by_sbm
        self.background_method = background_method

        self.name = f"Normalised to sbm + {normalise_by_sbm} + {self.background_method}"

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return other.normalise_by_sbm == self.normalise_by_sbm and \
               other.background_method == self.background_method

    def __hash__(self):
        return hash((self.normalise_by_sbm, self.background_method))
