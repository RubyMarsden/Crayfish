class Sample():
    def __init__(self, sample_name):
        self.spots = []
        self.name = sample_name
        self.is_standard = False

    def __repr__(self):
        return self.name