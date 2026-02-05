from src.diagram.description_models import DiagramContents, GBPMNDiagram, GBPMNElementType, GBPMNLane, GBPMNProcess


class DiagramBuilder:
    def __init__(self, data: DiagramContents):
        self.data = data

    def __elements(self, type):
        return [i for i in self.data.elements if i.type == type]

    def __call__(self) -> GBPMNDiagram:
        processes = []
        for p in self.__elements(GBPMNElementType.VIRT_PROC):
            lanes = [
                GBPMNLane(
                    id=l.id,
                    label=l.label,
                    bbox=l.bbox,
                    objects=[
                        o
                        for o in self.data.elements
                        if o.type not in {GBPMNElementType.VIRT_LANE,
                                          GBPMNElementType.VIRT_PROC} \
                           and o.id in l.nested_ids
                    ]
                )
                for l in self.__elements(GBPMNElementType.VIRT_LANE)
                if l.process_id == p.id
            ]
            processes.append(GBPMNProcess(
                id=p.id, label=p.label, bbox=p.bbox, lanes=lanes
            ))

        return GBPMNDiagram(
            processes=processes,
            flows={(i.source_id, i.target_id): i for i in self.data.links},
            objects={i.id: i for i in self.data.elements},
        )
