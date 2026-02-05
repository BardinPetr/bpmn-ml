import asyncio

import cv2
from ray import serve
from ray.serve.handle import DeploymentHandle

from src.diagram.annotate.binder import DiagramLinkBinder
from src.diagram.annotate.builder import DiagramBuilder
from src.diagram.annotate.description import make_description
from src.diagram.annotate.diagram import DiagramElementsGenerator
from src.diagram.annotate.graphgen import GraphBuilder
from src.diagram.annotate.labeler import Labeler
from src.diagram.annotate.nest import DiagramNestBinder
from src.diagram.ocr.main import OCRProcess
from src.diagram.struct.yolo import ObjectLineDetector
from src.ingress.api.model import FileData
from src.ingress.task.task_model import DiagramAnalyzeTaskRs
from src.renderer.codegen import GraphBPMNCodegen
from src.renderer.main import BPMNRendererService


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class DiagramAnalyzer:
    def __init__(self,
                 struct_detector: DeploymentHandle[ObjectLineDetector],
                 text_detector: DeploymentHandle[OCRProcess],
                 renderer: DeploymentHandle[BPMNRendererService]):
        self.struct_detector = struct_detector
        self.text_detector = text_detector
        self.renderer = renderer

    # async def __call__(self) -> DiagramAnalyzeTaskRs:
    #     lang = 'ru'
    #     img = cv2.imread(
    # "/home/petr/projects/mltests/dataset/out_image/0e5e7c91e225dd48e344d35c90e62fa7e867890268dd94df219d8b2eff0356aa.0.jpg")
    #     do_visualize = True

    async def __call__(self, img, do_visualize=False, lang=None) -> DiagramAnalyzeTaskRs:
        print(f"start analyze conf {do_visualize} {lang}")
        res = DiagramAnalyzeTaskRs()

        detector_out, ocr = await asyncio.gather(
            self.struct_detector.remote(img),
            self.text_detector.remote(img, lang),
        )
        # with open("a.json", "w") as f:
        #     f.write(detector_out.model_dump_json())
        # with open("b.json", "w") as f:
        #     f.write(ocr.model_dump_json())

        contents = DiagramElementsGenerator(detector_out)()
        contents = Labeler(detector_out, ocr).run(contents)
        contents = DiagramNestBinder(contents)()
        contents = DiagramLinkBinder(contents)()
        diagram = DiagramBuilder(contents)()

        res.files.append(FileData(
            data=diagram.model_dump_json().encode(),
            content_type="application/json",
            filename="diagram.json",
        ))
        with open("c.json", "w") as f:
            f.write(diagram.model_dump_json())

        graph_builder = GraphBuilder(contents, diagram)
        graph = graph_builder()

        res.description = make_description(diagram, graph)

        if do_visualize:
            graph_lay = graph_builder.create_layout()

            graph_vis_png = graph_builder.visualize()
            res.files.append(FileData(
                data=graph_vis_png,
                content_type="image/png",
                filename="graph.png",
            ))

            code = GraphBPMNCodegen()(graph, graph_lay, scale=2, target_size=(640, 480))
            # with open("code.txt", "w") as f:f.write(code)
            renders = await self.renderer.remote(code)

            res.files.append(FileData(
                data=renders['png'],
                content_type="image/png",
                filename="diagram.png",
            ))
            res.files.append(FileData(
                data=renders['svg'].encode(),
                content_type="image/svg+xml",
                filename="diagram.svg",
            ))
            res.files.append(FileData(
                data=renders['xml'].encode(),
                content_type="application/xml",
                filename="diagram.bpmn",
            ))

        res.success = True
        return res


app = DiagramAnalyzer.bind(ObjectLineDetector.bind(), OCRProcess.bind(), BPMNRendererService.bind())
