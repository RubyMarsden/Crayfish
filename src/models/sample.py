class Sample():
    def __init__(self, sample_name):
        self.spots = []
        self.name = sample_name
        self.is_standard = False
        self.WR_activity_ratio = None
        self.WR_activity_ratio_uncertainty = None

    def __repr__(self):
        return self.name
