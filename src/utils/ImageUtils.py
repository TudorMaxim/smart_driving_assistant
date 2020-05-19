import numpy as np
import torch.nn.functional as F
import torchvision.transforms as transforms


class ImageUtils:

    @staticmethod
    def pad_to_square(img, pad_value):
        c, h, w = img.shape
        dim_diff = np.abs(h - w)
        # (upper / left) padding and (lower / right) padding
        pad1, pad2 = dim_diff // 2, dim_diff - dim_diff // 2
        # Determine padding
        pad = (0, 0, pad1, pad2) if h <= w else (pad1, pad2, 0, 0)
        # Add padding
        img = F.pad(img, pad, "constant", value=pad_value)

        return img, pad

    @staticmethod
    def resize(image, size):
        image = F.interpolate(image.unsqueeze(0), size=size, mode="nearest").squeeze(0)
        return image

    @staticmethod
    def get_image_tensor(image, image_size=416):
        image = transforms.ToTensor()(image)
        image, _ = ImageUtils.pad_to_square(image, 0)  # Pad to square resolution
        image = ImageUtils.resize(image, image_size)  # Resize
        return image
