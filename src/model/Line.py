import numpy as np


class Line:
    def __init__(self):
        self.detected = False  # was the line detected in the last iteration?
        self.recent_xfitted = []  # x values of the last n fits of the line
        self.bestx = None  # average x values of the fitted line over the last n iterations
        self.recent_fits = []  # polynomial coefficients of last n iterations
        self.best_fit = None  # polynomial coefficients averaged over the last n iterations
        self.current_fit = [np.array([False])]  # polynomial coefficients for the most recent fit
        self.radius_of_curvature = None  # radius of curvature of the line in some units
        self.diffs = np.array([0, 0, 0], dtype='float')  # difference in fit coefficients between last and new fits
        self.allx = None  # x values for detected line pixels
        self.ally = None  # y values for detected line pixels
        self.num_missed = 0   # number of frames undetected

    def update_fit(self, fit, allx, ally, n_lines):
        # if there are to few points to rely on or a line wasn't detected
        if len(np.unique(ally)) < 100:
            self.num_missed += 1
            self.detected = False if self.num_missed > 20 else True
        # if everything was normal and a line was detected
        else:
            self.num_missed = 0
            self.detected = True
            self.current_fit = np.array(fit)
            self.allx = allx
            self.ally = ally
            self.recent_fits.append(fit)
            self.best_fit = np.average(self.recent_fits, axis=0)

            if len(self.recent_fits) > n_lines:
                self.recent_fits = self.recent_fits[-n_lines:]

            lowestx = allx[np.argmax(ally)]
            # keep n_lines amount of previus fits and use them to help compute the best fit
            self.recent_xfitted.append(lowestx)
            if len(self.recent_xfitted) > n_lines:
                self.recent_xfitted = self.recent_xfitted[-n_lines:]
            self.bestx = np.average(self.recent_xfitted)
