from src.diagram.annotate.tools import iou_metrics, rank
from src.diagram.description_models import DiagramContents, GBPMNElementType
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

    def resolve_external_label(self, bbox):
        return None

    def resolve_external_label_for_line(self, line):
        return None

    def resolve_label_for_process(self, obj):
        return None

    def resolve_label_for_pool(self, obj):
        return None

    def run(self, diag: DiagramContents) -> DiagramContents:
        out = diag.model_copy()
        for i in out.elements:
            if i.type == GBPMNElementType.TASK:
                i.label = self.resolve_internal_labels(i.bbox)
            if i.type == GBPMNElementType.VIRT_LANE:
                i.label = self.resolve_label_for_pool(i.bbox)
            if i.type == GBPMNElementType.VIRT_PROC:
                i.label = self.resolve_label_for_process(i.bbox)
            if i.type in {GBPMNElementType.GATEWAY,
                          GBPMNElementType.EVENT_START, GBPMNElementType.EVENT_END,
                          GBPMNElementType.EVENT_CATCH, GBPMNElementType.EVENT_THROW}:
                i.label = self.resolve_external_label(i.bbox)
        for i in out.links:
            i.label = self.resolve_external_label_for_line(i.line)
        return out
