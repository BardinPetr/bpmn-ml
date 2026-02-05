from typing import List, Set

import numpy as np

from src.diagram.annotate.matcher import iterative_matchA2B
from src.diagram.annotate.tools import iou_metrics, rank, get_bbox_center, get_links_coordinate, EVENT_TYPE_SET, \
    GATEWAY_TYPE_SET, get_bboxlist_centers
from src.diagram.description_models import DiagramContents, GBPMNElementType, GBPMNFlow, GBPMNElement, GBPMNDiagram
from src.diagram.ocr.model import OCROutput
from src.diagram.struct.model import DetectorOutput


class Labeler:
    def __init__(self, detector_data: DetectorOutput, ocr_data: OCROutput):
        self.detector_data = detector_data
        self.ocr_data = ocr_data
        self.label_pool = {i.bbox: i.text for i in self.ocr_data.texts}

    def resolve_internal_labels(self, bbox):
        if not len(self.label_pool): return None
        variants = rank(self.label_pool.items(), lambda x: iou_metrics(x[0], bbox)['inters_over_inner'], desc=True)
        variants = [i for r, i in variants if r > 0.9]
        # собираем текст в порядке чтения l->r, up->down
        variants = rank(variants, key=lambda i: i[0][1] + i[0][0] * 5000, desc=False)
        res = ""
        for r, (bb, txt) in variants:
            res += txt + " "
            self.label_pool.pop(bb)  # убираем из дальнейшего рассмотрения
        return res.strip() or None

    def resolve_label_for_process(self, obj):
        return None

    def resolve_label_for_pool(self, obj):
        return None

    def set_lines_labels(self, links: List[GBPMNFlow]):
        pass
        # label_bboxes = self.label_pool.keys()
        # label_coords = np.array(get_bboxlist_centers(label_bboxes))
        # lines_coords = np.array(get_links_coordinate(links))
        # mathes = iterative_matchA2B(lines_coords, label_coords)
        # print(label_coords)
        # print(lines_coords)
        # for label_idx, link_idx in mathes:
        #     label_bbox = label_bboxes[label_idx]
        #     links[link_idx].label = self.label_pool[label_bbox]
        #     del self.label_pool[label_bbox]

    def set_elements_labels(self, elements: List[GBPMNElement], type_set: Set[GBPMNElement]):
        pass
    #     label_bboxes = self.label_pool.values()
    #     label_coords, _ = get_bbox_center(label_bboxes)
    #
    #     items_coords, real_el_idx = get_bbox_center(elements, type_set)
    #
    #     mathes = iterative_matchA2B(items_coords, label_coords)
    #
    #     for label_idx, type_element_idx in mathes:
    #         element_idx = real_el_idx[type_element_idx]
    #
    #         label_bbox = label_bboxes[label_idx]
    #         elements[element_idx].label = self.label_pool[label_bbox]
    #         del self.label_pool[label_bbox]

    def run(self, diag: DiagramContents) -> DiagramContents:
        out = diag.model_copy()
        for i in out.elements:
            if i.type == GBPMNElementType.TASK:
                i.label = self.resolve_internal_labels(i.bbox)
            if i.type == GBPMNElementType.VIRT_LANE:
                i.label = self.resolve_label_for_pool(i.bbox)
            if i.type == GBPMNElementType.VIRT_PROC:
                i.label = self.resolve_label_for_process(i.bbox)
            # if i.type in {GBPMNElementType.GATEWAY,
            #               GBPMNElementType.EVENT_START, GBPMNElementType.EVENT_END,
            #               GBPMNElementType.EVENT_CATCH, GBPMNElementType.EVENT_THROW}:
            #     i.label = self.resolve_external_label(i.bbox)
        # for i in out.links:
        #     i.label = self.resolve_external_label_for_line(i.line)
        self.set_lines_labels(out.links)
        self.set_elements_labels(out.elements, EVENT_TYPE_SET)
        self.set_elements_labels(out.elements, GATEWAY_TYPE_SET)
        return out
