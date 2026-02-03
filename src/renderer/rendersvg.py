import cairosvg
from ray import serve

SIZE = (1920, 1080)


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class SVGRenderer:
    def __init__(self):
        pass

    def svg2png(self, svg: str) -> bytes:
        return cairosvg.svg2png(
            bytestring=svg.encode("utf8"),
            parent_width=SIZE[0],
            parent_height=SIZE[1],
            background_color="white",
        )


app = SVGRenderer.bind()
