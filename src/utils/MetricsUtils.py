import numpy as np
import torch
import tqdm

from utils.DetectionUtils import DetectionUtils


class MetricsUtils:
    @staticmethod
    def ap_per_class(tp, conf, pred_cls, target_cls):
        """ Compute the average precision, given the recall and precision curves.
        Source: https://github.com/rafaelpadilla/Object-Detection-Metrics.
        # Arguments
            tp:    True positives (list).
            conf:  Objectness value from 0-1 (list).
            pred_cls: Predicted object classes (list).
            target_cls: True object classes (list).
        # Returns
            The average precision as computed in py-faster-rcnn.
        """

        # Sort by objectness
        i = np.argsort(-conf)
        tp, conf, pred_cls = tp[i], conf[i], pred_cls[i]

        # Find unique classes
        unique_classes = np.unique(target_cls)

        # Create Precision-Recall curve and compute AP for each class
        ap, p, r = [], [], []
        for c in tqdm.tqdm(unique_classes, desc="Computing AP"):
            i = pred_cls == c
            n_gt = (target_cls == c).sum()  # Number of ground truth objects
            n_p = i.sum()  # Number of predicted objects

            if n_p == 0 and n_gt == 0:
                continue
            elif n_p == 0 or n_gt == 0:
                ap.append(0)
                r.append(0)
                p.append(0)
            else:
                # Accumulate FPs and TPs
                fpc = (1 - tp[i]).cumsum()
                tpc = (tp[i]).cumsum()

                # Recall
                recall_curve = tpc / (n_gt + 1e-16)
                r.append(recall_curve[-1])

                # Precision
                precision_curve = tpc / (tpc + fpc)
                p.append(precision_curve[-1])

                # AP from recall-precision curve
                ap.append(MetricsUtils.compute_ap(recall_curve, precision_curve))

        # Compute F1 score (harmonic mean of precision and recall)
        p, r, ap = np.array(p), np.array(r), np.array(ap)
        f1 = 2 * p * r / (p + r + 1e-16)

        return p, r, ap, f1, unique_classes.astype("int32")

    @staticmethod
    def compute_ap(recall, precision):
        """ Compute the average precision, given the recall and precision curves.
        Code originally from https://github.com/rbgirshick/py-faster-rcnn.
        # Arguments
            recall:    The recall curve (list).
            precision: The precision curve (list).
        # Returns
            The average precision as computed in py-faster-rcnn.
        """
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.0], recall, [1.0]))
        mpre = np.concatenate(([0.0], precision, [0.0]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
        return ap

    @staticmethod
    def get_batch_statistics(outputs, targets, iou_threshold):
        """ Compute true positives, predicted scores and predicted labels per sample """
        batch_metrics = []
        for sample_i in range(len(outputs)):

            if outputs[sample_i] is None:
                continue

            output = outputs[sample_i]
            pred_boxes = output[:, :4]
            pred_scores = output[:, 4]
            pred_labels = output[:, -1]

            true_positives = np.zeros(pred_boxes.shape[0])

            annotations = targets[targets[:, 0] == sample_i][:, 1:]
            target_labels = annotations[:, 0] if len(annotations) else []
            if len(annotations):
                detected_boxes = []
                target_boxes = annotations[:, 1:]

                for pred_i, (pred_box, pred_label) in enumerate(zip(pred_boxes, pred_labels)):

                    # If targets are found break
                    if len(detected_boxes) == len(annotations):
                        break

                    # Ignore if label is not one of the target labels
                    if pred_label not in target_labels:
                        continue

                    iou, box_index = DetectionUtils.bbox_iou(pred_box.unsqueeze(0), target_boxes).max(0)
                    if iou >= iou_threshold and box_index not in detected_boxes:
                        true_positives[pred_i] = 1
                        detected_boxes += [box_index]
            batch_metrics.append([true_positives, pred_scores, pred_labels])
        return batch_metrics

    @staticmethod
    def build_targets(pred_boxes, pred_cls, target, anchors, ignore_thres):

        ByteTensor = torch.cuda.ByteTensor if pred_boxes.is_cuda else torch.ByteTensor
        FloatTensor = torch.cuda.FloatTensor if pred_boxes.is_cuda else torch.FloatTensor

        nB = pred_boxes.size(0)
        nA = pred_boxes.size(1)
        nC = pred_cls.size(-1)
        nG = pred_boxes.size(2)

        # Output tensors
        obj_mask = ByteTensor(nB, nA, nG, nG).fill_(0)
        noobj_mask = ByteTensor(nB, nA, nG, nG).fill_(1)
        class_mask = FloatTensor(nB, nA, nG, nG).fill_(0)
        iou_scores = FloatTensor(nB, nA, nG, nG).fill_(0)
        tx = FloatTensor(nB, nA, nG, nG).fill_(0)
        ty = FloatTensor(nB, nA, nG, nG).fill_(0)
        tw = FloatTensor(nB, nA, nG, nG).fill_(0)
        th = FloatTensor(nB, nA, nG, nG).fill_(0)
        tcls = FloatTensor(nB, nA, nG, nG, nC).fill_(0)

        # Convert to position relative to box
        target_boxes = target[:, 2:6] * nG
        gxy = target_boxes[:, :2]
        gwh = target_boxes[:, 2:]
        # Get anchors with best iou
        ious = torch.stack([DetectionUtils.bbox_wh_iou(anchor, gwh) for anchor in anchors])
        best_ious, best_n = ious.max(0)
        # Separate target values
        b, target_labels = target[:, :2].long().t()
        gx, gy = gxy.t()
        gw, gh = gwh.t()
        gi, gj = gxy.long().t()
        # Set masks
        obj_mask[b, best_n, gj, gi] = 1
        noobj_mask[b, best_n, gj, gi] = 0

        # Set noobj mask to zero where iou exceeds ignore threshold
        for i, anchor_ious in enumerate(ious.t()):
            noobj_mask[b[i], anchor_ious > ignore_thres, gj[i], gi[i]] = 0

        # Coordinates
        tx[b, best_n, gj, gi] = gx - gx.floor()
        ty[b, best_n, gj, gi] = gy - gy.floor()
        # Width and height
        tw[b, best_n, gj, gi] = torch.log(gw / anchors[best_n][:, 0] + 1e-16)
        th[b, best_n, gj, gi] = torch.log(gh / anchors[best_n][:, 1] + 1e-16)
        # One-hot encoding of label
        tcls[b, best_n, gj, gi, target_labels] = 1
        # Compute label correctness and iou at best anchor
        class_mask[b, best_n, gj, gi] = (pred_cls[b, best_n, gj, gi].argmax(-1) == target_labels).float()
        iou_scores[b, best_n, gj, gi] = DetectionUtils.bbox_iou(pred_boxes[b, best_n, gj, gi], target_boxes, x1y1x2y2=False)

        tconf = obj_mask.float()
        return iou_scores, class_mask, obj_mask, noobj_mask, tx, ty, tw, th, tcls, tconf