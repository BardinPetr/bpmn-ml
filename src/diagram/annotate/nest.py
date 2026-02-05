from src.diagram.annotate.tools import rank, iou_metrics, buid
from src.diagram.description_models import *

AGGREGATED_ETYPES = {GBPMNElementType.VIRT_LANE, GBPMNElementType.VIRT_PROC}


class DiagramNestBinder:

    def __init__(self, data: DiagramContents):
        self.data = data.model_copy()
        self.basic_elements = [i
                               for i in self.data.elements
                               if i.type not in AGGREGATED_ETYPES]

    def __scan_internals(self, bbox, source=None, cutoff=0.9):
        variants = rank(source or self.basic_elements,
                        lambda x: iou_metrics(x.bbox, bbox)['inters_over_inner'],
                        desc=True)
        return [i for r, i in variants if r > cutoff]

    def __processes(self):
        return [i for i in self.data.elements if i.type == GBPMNElementType.VIRT_PROC]

    def __lanes(self):
        return [i for i in self.data.elements if i.type == GBPMNElementType.VIRT_LANE]

    def __call__(self) -> DiagramContents:
        # находим лэйны в процессах
        # добавляем единственный дефолтный лэйн если ни одного нет
        # для лэйнов находим содержимое
        # связываем процессы, лэйны и содержимое
        for proc in self.__processes():
            lanes = self.__scan_internals(proc.bbox, source=self.__lanes(), cutoff=0.7)
            if not lanes:
                lanes = [GBPMNElement(
                    id=str(buid("Lane")),
                    label=proc.label,
                    type=GBPMNElementType.VIRT_LANE,
                    bbox=proc.bbox,
                )]

            lids = []
            for lane in lanes:
                lid = lane.id
                lane_content = self.__scan_internals(lane.bbox, source=self.basic_elements, cutoff=0.9)
                lane = GBPMNLaneElement(**{**lane.model_dump(),
                                           "process_id": proc.id,
                                           "nested_ids": [i.id for i in lane_content]})
                lids.append(lid)
                self.data.drop(lid)
                self.data.add(lane)

            proc = GBPMNProcessElement(**proc.model_dump(), lanes_ids=lids)
            self.data.drop(proc.id)
            self.data.add(proc)

        return self.data
