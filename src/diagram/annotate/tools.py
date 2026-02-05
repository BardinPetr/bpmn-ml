import math
from typing import List

from src.diagram.description_models import GBPMNElementType, GBPMNElement, GBPMNFlow


def iou_metrics(inner, outer):
    xA = max(inner[0], outer[0])
    yA = max(inner[1], outer[1])
    xB = min(inner[2], outer[2])
    yB = min(inner[3], outer[3])
    intersect = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    a_area = (inner[2] - inner[0] + 1) * (inner[3] - inner[1] + 1)
    b_area = (outer[2] - outer[0] + 1) * (outer[3] - outer[1] + 1)
    return dict(
        intersect=intersect,
        a_area=a_area,
        b_area=b_area,
        # сколько занимает пересечение от объединения
        iou=intersect / float(a_area + b_area - intersect),
        # сколько занимает площадь пересечения относительно площади внутреннего (inner) - 1.0 показывает что весь inner в outer
        inters_over_inner=intersect / a_area
    )


def rank(data, key, desc=True):
    data = [(key(i), i) for i in data]
    return sorted(data, key=lambda i: i[0], reverse=desc)


def bbox_center(bbox):
    return (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2


def bbox_lines(bbox):
    x0, y0, x1, y1 = bbox
    tl, tr = (x0, y0), (x1, y0)
    bl, br = (x0, y1), (x1, y1)
    return [
        (tl, tr),
        (tr, br),
        (br, bl),
        (bl, tl)
    ]


def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def dist_pt2line(point, line):
    px, py = point
    (x1, y1), (x2, y2) = line
    dx, dy = x2 - x1, y2 - y1
    t = ((px - x1) * dx + (py - y1) * dy) / (dx ** 2 + dy ** 2)
    t = max(0, min(1, t))
    near = x1 + t * dx, y1 + t * dy
    return dist(point, near)


def dist_pt2bbox(point, bbox):
    return min(dist_pt2line(point, i) for i in bbox_lines(bbox))


EVENT_TYPE_SET = {
    GBPMNElementType.EVENT_START,
    GBPMNElementType.EVENT_END,
    GBPMNElementType.EVENT_CATCH,
    GBPMNElementType.EVENT_THROW,
}

GATEWAY_TYPE_SET = {GBPMNElementType.GATEWAY}


def get_bbox_center(elements: List[GBPMNElement], type: GBPMNElementType = None):
    coord_list = list()
    idx_list = list()
    for i, el in enumerate(elements):
        if type is not None:
            if el.type not in type:
                continue
        x1, y1, x2, y2 = el.bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        coord_list.append(
            [center_x, center_y]
        )
        idx_list.append(i)
    return coord_list, idx_list


def get_bboxlist_centers(bboxes: List):
    coord_list = list()
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        coord_list.append(
            [center_x, center_y]
        )
    return coord_list


def get_links_coordinate(links: List[GBPMNFlow]):
    return [link.line for link in links]
