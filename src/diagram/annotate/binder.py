from src.diagram.annotate.tools import dist_pt2bbox, rank
from src.diagram.description_models import DiagramContents, GBPMNElementType

MAX_LINK2OBJ_DISTANCE = 10


class DiagramLinkBinder:

    def __init__(self, data: DiagramContents):
        self.data = data.model_copy()
        self.linkable = [i
                         for i in self.data.elements
                         if i.type not in {GBPMNElementType.VIRT_LANE}]

    def __search_near(self, pos):
        variants = rank(self.linkable, lambda x: dist_pt2bbox(pos, x.bbox), desc=False)
        variants = [i for r, i in variants if r < MAX_LINK2OBJ_DISTANCE]
        return variants[0] if variants else None

    def __call__(self) -> DiagramContents:
        old_count = len(self.data.links)
        links = []
        for i in self.data.links:
            if i.source_id and i.target_id: continue
            s, t = self.__search_near(i.line[0]), self.__search_near(i.line[-1])
            if not s or not t: continue
            i.source_id = s.id
            i.target_id = t.id
            links.append(i)
        self.data.links = links
        new_count = len(links)
        if new_count != old_count:
            print(f"links dropped {old_count} -> {new_count}")
        return self.data
