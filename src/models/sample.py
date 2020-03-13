class Sample():
    def __init__(self, sample_name):
        self.spots = []
        self.name = sample_name

    def __repr__(self):
        return self.name