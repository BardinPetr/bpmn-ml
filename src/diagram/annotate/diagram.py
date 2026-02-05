from src.diagram.annotate.tools import buid, cfirst
from src.diagram.description_models import DiagramContents, GBPMNElement, GBPMNElementType, GBPMNElementSubType, \
    GBPMNFlowType, GBPMNFlow
from src.diagram.struct.model import DetectorOutput, DetectorObjectType, DetectorLineType, DetectorObject, DetectorLine

DOT2ET = {
    DetectorObjectType.EVENT_START: GBPMNElementType.EVENT_START,
    DetectorObjectType.EVENT_END: GBPMNElementType.EVENT_END,
    DetectorObjectType.EVENT_THROW: GBPMNElementType.EVENT_THROW,
    DetectorObjectType.EVENT_CATCH: GBPMNElementType.EVENT_CATCH,
    DetectorObjectType.GATEWAY_PARALLEL: GBPMNElementType.GATEWAY,
    DetectorObjectType.GATEWAY_INCLUSIVE: GBPMNElementType.GATEWAY,
    DetectorObjectType.GATEWAY_EXCLUSIVE: GBPMNElementType.GATEWAY,
    DetectorObjectType.GATEWAY_EVENT_BASED: GBPMNElementType.GATEWAY,
    DetectorObjectType.TASK: GBPMNElementType.TASK,
    DetectorObjectType.LANE: GBPMNElementType.VIRT_LANE,
    DetectorObjectType.PROCESS: GBPMNElementType.VIRT_PROC
}

DOT2EST = {
    DetectorObjectType.GATEWAY_PARALLEL: GBPMNElementSubType.GATEWAY_PARALLEL,
    DetectorObjectType.GATEWAY_INCLUSIVE: GBPMNElementSubType.GATEWAY_INCLUSIVE,
    DetectorObjectType.GATEWAY_EXCLUSIVE: GBPMNElementSubType.GATEWAY_EXCLUSIVE,
    DetectorObjectType.GATEWAY_EVENT_BASED: GBPMNElementSubType.GATEWAY_EVENT
}

DLT2FT = {
    DetectorLineType.SEQUENCE: GBPMNFlowType.SEQUENCE,
    DetectorLineType.MESSAGE: GBPMNFlowType.MESSAGE
}


class DiagramElementsGenerator:

    def __init__(self, detector_data: DetectorOutput):
        self.detector_data = detector_data

    def __o_type(self, x: DetectorObject):
        if res := DOT2ET.get(x.type, None):
            return res
        return None

    def __o_subtype(self, type, x):
        if type == GBPMNElementType.TASK:
            return GBPMNElementSubType.TASK_OTHER
        if type == GBPMNElementType.GATEWAY:
            return DOT2EST.get(type, GBPMNElementSubType.GATEWAY_EXCLUSIVE)
        if type in {GBPMNElementType.EVENT_START,
                    GBPMNElementType.EVENT_THROW,
                    GBPMNElementType.EVENT_CATCH,
                    GBPMNElementType.EVENT_END}:
            return GBPMNElementSubType.EVENT_OTHER
        return None

    def __l_type(self, x: DetectorLine):
        if res := DLT2FT.get(x.type, None):
            return res
        return None

    def __call__(self) -> DiagramContents:
        out = DiagramContents(elements=[], links=[])
        for i in self.detector_data.objects:
            typ = self.__o_type(i)
            out.elements.append(GBPMNElement(
                id=buid(cfirst(typ.value.replace("_", ""))),
                type=typ,
                subtype=self.__o_subtype(typ, i),
                bbox=i.bbox
            ))
        for i in self.detector_data.lines:
            out.links.append(GBPMNFlow(
                id=buid("Flow"),
                type=self.__l_type(i),
                line=i.line
            ))

        return out
