
class XDFStream:
    def __init__(self):
        self.time_series = [['{"stimulus_idx": "476", "stim_type": "PVT", "freq": "8", "phase": "135"}'],
                             ['{"reaction_time": "199"}'],
                             ['{"stimulus_idx": "477", "stim_type": "PVT", "freq": "8", "phase": "225"}'],
                             ['{"reaction_time": "192"}'],
                             ['{"stimulus_idx": "478", "stim_type": "TMS", "freq": "12", "phase": "225"}'],
                             ['{"stimulus_idx": "479", "stim_type": "PVT", "freq": "28", "phase": "135"}'],
                             ['{"reaction_time": "206"}'],
                             ['{"stimulus_idx": "480", "stim_type": "TMS", "freq": "16", "phase": "180"}']]
        self.time_stamps = [205870.74691046, 205874.48103644, 205876.26009724, 205878.62251455,
                            205880.14181628, 205882.52401438, 205886.67367042, 205890.22252488]