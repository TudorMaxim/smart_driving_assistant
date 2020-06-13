import pickle
import cv2
import numpy as np
from model.Image import Image
from model.Line import Line
from utils.Constants import Constants


class LaneDetectionController:
    def __init__(self,  plot=False, direction_error=15):
        self.calibration_file = Constants.ROOT_PATH + 'config/calibration.pickle'
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = self.__calibrate()
        self.left_line = Line()
        self.right_line = Line()
        self.plot = plot
        self.direction_error = direction_error

    def __calibrate(self):
        file = open(self.calibration_file, 'rb')
        ret, mtx, dist, rvecs, tvecs = pickle.load(file)
        return ret, mtx, dist, rvecs, tvecs

    def __get_radius(self, polyfit_left, polyfit_right):
        if polyfit_left is None or polyfit_right is None:
            return 0, 0, 0

        ploty = np.linspace(0, 719, num=720)  # to cover same y-range as image
        y_eval = np.max(ploty)
        # define conversions in x and y from pixels space to meters
        ym_per_pix = 30 / 720  # meters per pixel in y dimension
        xm_per_pix = 3.7 / 600  # meters per pixel in x dimension
        leftx = polyfit_left[0] * ploty ** 2 + polyfit_left[1] * ploty + polyfit_left[2]
        rightx = polyfit_right[0] * ploty ** 2 + polyfit_right[1] * ploty + polyfit_right[2]
        # fit new polynomials to x,y in world space
        left_fit_cr = np.polyfit(ploty * ym_per_pix, leftx * xm_per_pix, 2)
        right_fit_cr = np.polyfit(ploty * ym_per_pix, rightx * xm_per_pix, 2)
        # Calculate the new radius of curvature
        left_curverad = ((1 + (2 * left_fit_cr[0] * y_eval * ym_per_pix + left_fit_cr[1]) ** 2) ** 1.5) / \
                        np.absolute(2 * left_fit_cr[0])
        right_curverad = ((1 + (2 * right_fit_cr[0] * y_eval * ym_per_pix + right_fit_cr[1]) ** 2) ** 1.5) / \
                         np.absolute(2 * right_fit_cr[0])

        avg_curvature = round(np.mean([left_curverad, right_curverad]), 0)

        middle = 640
        l_base_pos = 720 * polyfit_left[0] ** 2 + 720 * polyfit_left[1] + polyfit_left[2]
        r_base_pos = 720 * polyfit_right[0] ** 2 + 720 * polyfit_right[1] + polyfit_right[2]
        lane_center = (r_base_pos + l_base_pos) / 2
        offset = (middle - lane_center) * xm_per_pix
        if abs(offset) < 0.1:
            offset = 0
        return avg_curvature, offset

    def __get_direction(self, left_fit, right_fit):
        ploty = np.linspace(0, 719, 720)
        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
        diff_left = left_fitx[0] - left_fitx[719]
        diff_right = right_fitx[0] - right_fitx[719]
        diff = (diff_left + diff_right) / 2
        if abs(diff) < self.direction_error:
            return 'straight'
        elif diff > self.direction_error:
            return 'right'
        return 'left'

    def detect(self, image):
        img = Image(image, 'rgb')
        undist = img.undistort(self.mtx, self.dist)
        n_lines = 15
        try:
            # convert to binary top down view of the lane lines and apply sobel
            binary, inv_matrix = undist.binary_warp(plot=self.plot)
            if self.right_line.detected and self.left_line.detected:
                left_fit, right_fit, leftx, rightx, lefty, righty = binary.find_lines_based_on_previous(
                    self.left_line.best_fit,
                    self.right_line.best_fit
                )
            else:
                left_fit, right_fit, leftx, rightx, lefty, righty = binary.find_lines()

            self.right_line.update_fit(right_fit, rightx, righty, n_lines)
            self.left_line.update_fit(left_fit, leftx, lefty, n_lines)

            if self.right_line.detected and self.left_line.detected:
                warped = binary
                warp_zero = np.zeros_like(warped).astype(np.uint8)
                color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
                left_fit = self.left_line.best_fit
                right_fit = self.right_line.best_fit
                curvature, position = self.__get_radius(left_fit, right_fit)
                direction = self.__get_direction(self.left_line.best_fit, self.right_line.best_fit)

                ploty = np.linspace(0, 719, num=720)
                left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
                right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
                # recast the x and y points into usable format for cv2.fillPoly()
                pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
                pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
                pts = np.hstack((pts_left, pts_right))
                # draw the lane onto the warped blank image
                cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))
                # warp the blank back to original image space using inverse perspective matrix (inv_matrix)
                newwarp = cv2.warpPerspective(color_warp, inv_matrix, (img.img.shape[1], img.img.shape[0]))
                # combine the result with the original image
                result = cv2.addWeighted(undist.img, 1, newwarp, 0.3, 0)

                cv2.putText(result, "Average curvature: %.1f m." % curvature, (50, 70), cv2.FONT_HERSHEY_DUPLEX, 1,
                            (255, 255, 255), 2)
                cv2.putText(result, "Lane direction: %s." % direction, (50, 120), cv2.FONT_HERSHEY_DUPLEX, 1,
                            (255, 255, 255), 2)

                position = round(position, 1)
                if position == 0:
                    cv2.putText(result, "Off the center: %.1f m." % position, (50, 170), cv2.FONT_HERSHEY_DUPLEX, 1,
                                (255, 255, 255), 2)
                else:
                    offset_dir = 'to the left.' if position < 0 else 'to the right.'
                    cv2.putText(result, "Off the center: " + str(abs(position)) + "m " + offset_dir, (50, 170),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                return result
            else:
                return undist.img
        except:
            return undist.img

    def process_image(self, image):
        self.left_line = Line()
        self.right_line = Line()
        return self.detect(image)

    def process_video(self, frame):
        return self.detect(frame)
