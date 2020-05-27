import numpy as np
import cv2
import matplotlib.pyplot as plt


class Image:
    def __init__(self, img=None, form='rgb'):
        if form == 'bgr':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            form = 'rgb'
        self.img = img
        self.form = form
        self.shape = 0
        self.img = cv2.resize(self.img, (1280, 720), interpolation=cv2.INTER_AREA)

    def imshow(self, title=None):
        img = self.img
        plt.figure()
        if len(img.shape) > 2:
            if self.form == 'hls':
                img = cv2.cvtColor(img, cv2.COLOR_HLS2RGB)
            if self.form == 'hsv':
                img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
            plt.imshow(img)
        else:
            plt.imshow(img, cmap='gray')
        if title:
            plt.title(title)
        plt.show()
        return

    # lets an instance of the class be interpreted as an array
    def __array__(self):
        return np.array(self.img)

    def __getitem__(self, key):
        return self.img[key]

    # undisort an image using the distortion matrixes
    def undistort(self, mtx, dist):
        img = self.img
        dst = cv2.undistort(img, mtx, dist, None, mtx)
        return Image(dst, form=self.form)

    # apply gaussian blur
    def gausian_blur(self, ksize=5):
        img = self.img
        blur = cv2.GaussianBlur(img, (ksize, ksize), 0)
        return Image(blur, form=self.form)

    # change the color format, can choose gray, hsv, or hls, and can pick a particular channel that you want
    def format(self, form='gray', channel=None):
        if self.form != 'rgb':
            raise Exception("Don't go trying to convert from a none RGB image now you hear.")
        img = self.img
        if form == 'gray':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        elif form == 'hls':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
            if channel == 'h':
                img = img[:, :, 0]
            if channel == 'l':
                img = img[:, :, 1]
            if channel == 's':
                img = img[:, :, 2]

        elif form == 'hsv':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            if channel == 'h':
                img = img[:, :, 0]
            if channel == 's':
                img = img[:, :, 1]
            if channel == 'v':
                img = img[:, :, 2]

        if len(img.shape) < 3:
            form = 'gray'
        return Image(img, form=form)

    # run sobel operation on either x or y axis.
    def sobel_thresh(self, orient='x', ksize=5, thresh=(50, 255)):
        img = self.img
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Calculate directional gradient
        abs_sobel = None
        if orient == 'x':
            abs_sobel = np.absolute(cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize))
        if orient == 'y':
            abs_sobel = np.absolute(cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize))
        scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
        # Apply threshold
        grad_binary = np.zeros_like(scaled_sobel)
        grad_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
        img = grad_binary
        return Image(img, form='gray')

    # return binary image of sobel direction between thresh values
    # ksize indicate size of sobel kernals
    def dir_threshold(self, ksize=5, thresh=(.7, 1.3)):
        img = self.img
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Take the gradient in x and y separately
        sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize)
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize)
        # Take the absolute value of the x and y gradients
        abs_sobelx = np.absolute(sobel_x)
        abs_sobely = np.absolute(sobel_y)
        # calculate the direction of the gradient
        grad_dir = np.arctan2(abs_sobely, abs_sobelx)
        # Create a binary mask where direction thresholds are met
        grad_binary = np.zeros_like(grad_dir)
        grad_binary[(grad_dir >= thresh[0]) & (grad_dir <= thresh[1])] = 1
        img = grad_binary
        return Image(img, form='gray')

    # returns binary image of sobel magnitude between mag_thresh values
    # ksize sets size of sobel kernals
    def mag_thresh(self, ksize=5, mag_thresh=(50, 255)):
        img = self.img
        # if not grey image, convert to grey
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # perform sobel operation on image in both directions
        abs_sobelx = np.absolute(cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize))
        abs_sobely = np.absolute(cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize))
        # get magnitude of all points
        sobel_mag = np.sqrt((abs_sobelx ** 2) + (abs_sobely ** 2))
        # scale magnitude to range of 0-255
        scale_factor = np.max(sobel_mag) / 255
        sobel_scaled = (sobel_mag / scale_factor).astype(np.uint8)
        # Apply threshold
        grad_binary = np.zeros_like(sobel_scaled)
        grad_binary[(sobel_scaled >= mag_thresh[0]) & (sobel_scaled <= mag_thresh[1])] = 1
        img = grad_binary
        return Image(img, form='gray')

    # produce a picture from all places where both binary pictures have 1's
    def image_and(self, img2):
        if self.img is None:
            raise Exception("class doesn't contain an image")
        img1 = self.img

        # if being passed an image class, grab the image to use.
        if type(self) == type(img2):
            img2 = img2.img
        # check that the images are valid for the -and- function
        if img1.shape != img2.shape:
            raise Exception("shapes must be equal to preform and operation")
        if (np.max(img1) > 1) | (np.max(img2) > 1):
            raise Exception("and operation doesn't work on non-binary images")

        # create image where all shared white pixels are set to 1
        output = np.zeros_like(img1)
        output[(img1 == 1) & (img2 == 1)] = 1
        img = output
        return Image(img=img, form='gray')

    # produce a picture from all places where either binary picture has a value of 1
    def image_or(self, img2):
        if self.img is None:
            raise Exception("class doesn't contain an image")
        img1 = self.img
        # if being passed an image class, grab the image to use.
        if type(self) == type(img2):
            img2 = img2.img
        # check that the images are valid for the -and- function
        if img1.shape != img2.shape:
            raise Exception("shapes must be equal to preform or operation")
        if (np.max(img1) > 1) | (np.max(img2) > 1):
            raise Exception("or operation doesn't work on non-binary images")
        # create image where all white pixels from either image are set to 1
        output = np.zeros_like(img1)
        output[(img1 == 1) | (img2 == 1)] = 1
        img = output
        return Image(img=img, form='gray')

    # transform perspective to aerial view
    # src is the source points for the transform, dst is the destination point
    # returns image and inverse transformation matrix
    def transform(self, src=None, dst=None, img_size=(1280, 720)):
        img = self.img
        # use default transformation points if non were passed
        if not src:
            src = np.float32([[696, 455],
                             [1096, 719],
                             [206, 719],
                             [587, 455]])
        if not dst:
            dst = np.float32([[930, 0],
                             [930, 719],
                             [350, 719],
                             [350, 0]])

        matrix = cv2.getPerspectiveTransform(src, dst)  # get transformation matrix
        inv_matrix = cv2.getPerspectiveTransform(dst, src)  # get inverse transformation matrix
        warped = cv2.warpPerspective(img, matrix, img_size, flags=cv2.INTER_LINEAR)  # warp perspective
        output = Image(warped)
        return output, inv_matrix

    def region_of_interest(self, vertices=None):
        img = self.img
        imshape = (img.shape[1], img.shape[0])
        # make default vertices if none was passed
        if vertices is None:
            vertices = np.array([[(0, imshape[1]),
                                (int(imshape[0] * .45), int(imshape[1] * .5)),
                                (int(imshape[0] * .55), int(imshape[1] * .5)),
                                (imshape[0], imshape[1])]],
                                dtype=np.int32)

        # defining a blank mask to start with
        mask = np.zeros_like(img)
        # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
        if len(img.shape) > 2:
            channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255
        # filling pixels inside the polygon defined by "vertices" with the fill color
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        # returning the image only where mask pixels are nonzero
        masked_image = cv2.bitwise_and(img, mask)
        output = Image(masked_image, form=self.form)
        return output

    # uses class functions to turn rgb image into warped binary image
    # returns the image and inverse transformation matrix
    def binary_warp(self, plot=False):
        # apply Gaussian Blur
        blur = self.gausian_blur(ksize=5)
        # create new grey images using only one hls channel
        l = blur.format('hls', 'l')
        s = blur.format('hls', 's')
        # calculate directional threshhold
        dir_thresh = blur.dir_threshold(ksize=9, thresh=(.7, 1.3))
        # calculate magnitude threshhold
        mag_thresh = blur.mag_thresh(ksize=5, mag_thresh=(50, 255))
        # combine both images with and operation
        magdir = mag_thresh.image_and(dir_thresh)
        # preform sobel operation on several image channels and axis
        lx = l.sobel_thresh(orient='x', ksize=5, thresh=(40, 100))
        sx = s.sobel_thresh(orient='x', ksize=5, thresh=(25, 255))
        sy = s.sobel_thresh(orient='y', ksize=5, thresh=(30, 100))
        # combine all images to get the clearest binary img of the lines
        sxy = sx.image_and(sy)
        lsxy = sxy.image_or(lx)
        both = lsxy.image_or(magdir)
        crop = both.region_of_interest()
        binary_warped, inverse_matrix = crop.transform()
        if plot:
            blur.imshow('blur')
            both.imshow('after sobel')
            crop.imshow('region of interest')
            binary_warped.imshow('result')
        return binary_warped, inverse_matrix

    # find the coefficients for the left and right lines and return them along with the indices of all points on them
    # margin sets the number of pixels to the left and right of the base of each line that will be included in a window
    # minpix is the number of pixels a window must have to be accepted as part of the line
    def find_lines(self, margin=100, minpix=200):
        img = self.img
        shape = img.shape
        # narrow image down to only bottom half
        bottom = img[int(shape[0] / 2):, :]
        # create histogram of frequency of points along the y axis to find starting place for search
        hist = np.sum(bottom, axis=0)
        # find base of windows
        middle = np.int(shape[1] / 2)
        leftx_base = np.argmax(hist[:middle])
        rightx_base = np.argmax(hist[middle:]) + middle
        leftx_current = leftx_base
        rightx_current = rightx_base
        # Set height of windows
        windows_cnt = 15
        window_height = np.int(shape[0] / windows_cnt)
        # Identify the x and y positions of all nonzero pixels in the image
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        # create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        for window in range(windows_cnt):
            # find points for window rectangles
            win_y_low = shape[0] - ((window + 1) * window_height)
            win_y_high = shape[0] - (window * window_height)
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # identify the nonzero pixels in x and y within the window
            good_left_inds = (
                    (nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                    (nonzerox >= win_xleft_low) &
                    (nonzerox < win_xleft_high)
            ).nonzero()[0]
            good_right_inds = (
                    (nonzeroy >= win_y_low) &
                    (nonzeroy < win_y_high) &
                    (nonzerox >= win_xright_low) &
                    (nonzerox < win_xright_high)
            ).nonzero()[0]
            # append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # if the window had enough pixels in it, add it to the array
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
        # concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        # extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        # fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        return left_fit, right_fit, leftx, rightx, lefty, righty

    # find the coefficients for the left and right lines and return them along with the indices of all points on them
    # margin sets the number of pixels to the left and right of the base of each line that will be included in a window
    # function must take already fitted lines produced by "find_lines"
    def find_lines_based_on_previous(self, left_fit, right_fit, margin=100):
        img = self.img
        # find all non zero pixels within the fitted lanes
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        left_lane_inds = (
            (nonzerox > (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] - margin)) &
            (nonzerox < (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] + margin))
        )
        right_lane_inds = (
            (nonzerox > (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] - margin)) &
            (nonzerox < (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] + margin))
        )
        # again, extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        # fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        return left_fit, right_fit, leftx, rightx, lefty, righty
