import asyncio

import cv2
from ray import serve
from ray.serve.handle import DeploymentHandle
from rich import print

from src.diagram.ocr.main import OCRProcess
from src.diagram.ocr.model import OCRResult
from src.diagram.struct.model import DetectorOutput
from src.diagram.struct.yolo import ObjectLineDetector


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class DiagramAnalyzer:
    def __init__(self,
                 struct_detector: DeploymentHandle[ObjectLineDetector],
                 text_detector: DeploymentHandle[ObjectLineDetector],
                 ):
        self.struct_detector = struct_detector
        self.text_detector = text_detector
        asyncio.get_event_loop().create_task(self())

    async def __call__(self):
        img = cv2.imread(
            "/home/petr/projects/mltests/dataset/out_image/0e5e7c91e225dd48e344d35c90e62fa7e867890268dd94df219d8b2eff0356aa.0.jpg")

        detector_out, ocr = await asyncio.gather(
            self.struct_detector.remote(img),
            self.text_detector.remote(img),
        )

        for i in detector_out.lines:
            print(i.type.name, i.line)
        for i in detector_out.objects:
            print(i.type.name, i.bbox)
        print(ocr)


app = DiagramAnalyzer.bind(ObjectLineDetector.bind(), OCRProcess.bind())
