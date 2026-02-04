# import gradio as gr
# import asyncio
# import uuid
# from datetime import datetime
# from typing import List
# import time
#
# import ray
# from fastapi import FastAPI
# from ray import serve
#
#
# def fastapi_factory():
#     app = FastAPI()
#
#     # handler = serve.get_deployment_handle("ChildDeployment", app_name="default")
#     # return await handler.remote(x)
#
#     """
#     async def submit_images(images: List) -> tuple:
#         if not images:
#             return None, "Please upload at least one image", []
#
#         print(images)
#         tasks = []
#         # for img_path in images:
#         #     with open(img_path, 'rb') as f:
#         #         img_data = f.read()
#             # tasks.append(TaskDataD2T(
#             #     image=FileData(
#             #         data=img_data,
#             #         content_type='image/jpeg'  # Adjust as needed
#             #     ),
#             #     props={}
#             # ))
#
#         request_id = str(uuid.uuid4())
#         submitted_at = datetime.now()
#         # await self.task_service.new_request.remote(InternalTaskBlock(
#         #     request_id=request_id,
#         #     submitted_at=submitted_at,
#         #     tasks=tasks,
#         #     subsystem=SubsystemType.DIAG2TXT,
#         # ))
#         #
#         return f"Submitted {len(images)} images", []
#
#     async def run(images, progress=gr.Progress()):
#         await submit_images(images)
#         progress(0.1, desc="status_msgc")
#         await asyncio.sleep(1)
#         yield "st1", "text",
#         progress(0.8, desc="status_msgc")
#         await asyncio.sleep(1)
#         return "DONE", []
#
#     def gradio_builder():
#         with gr.Blocks(title="BPMN to description") as site:
#             gr.Markdown("# Analyze BPMN image")
#             gr.Markdown("Upload multiple images for processing")
#
#             with gr.Row():
#                 with gr.Column(scale=1):
#                     image_input = gr.File(
#                         file_count="multiple",
#                         file_types=["image"],
#                         label="Upload Images"
#                     )
#                     submit_btn = gr.Button("Submit", variant="primary")
#
#                 with gr.Column(scale=1):
#                     status_output = gr.Textbox(
#                         label="Status",
#                         lines=3,
#                         interactive=False
#                     )
#                     results_output = gr.JSON(
#                         label="Results",
#                         visible=True
#                     )
#
#             submit_btn.click(
#                 fn=run,
#                 inputs=[image_input],
#                 outputs=[status_output, results_output]
#             )
#
#         return site
#
#     """
#
#     gr.mount_gradio_app(app, gradio_builder(), path="/")
#
#     return app
#
#
# @serve.deployment
# @serve.ingress(fastapi_factory)
# class ParentDeployment:
#     def __init__(self):
#         pass
#
# ray.init()
#
# serve.run(ParentDeployment.bind())
#
# while True:
#     pass


import asyncio
import random
from enum import Enum
from io import BytesIO
from typing import Optional, Any, List

import gradio as gr
from PIL import Image, ImageOps
from pydantic import BaseModel


# Define the models and enums
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResult(BaseModel):
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    files: Optional[List[tuple]] = None  # List of (filename, type, file_data) as tuples


# Simulate a database for tasks (in a real scenario, this would be persistent storage)
dummy_tasks = {}


# Mock async queue_task function
async def queue_task(img: Image.Image) -> str:
    task_id = str(random.randint(1000, 9999))
    dummy_tasks[task_id] = TaskResult(status=TaskStatus.PENDING)
    asyncio.create_task(process_task(task_id, img))
    return task_id


# Mock task processing function (simulates async work)
async def process_task(task_id: str, img: Image.Image):
    await asyncio.sleep(2)  # Simulate processing time
    # Generate mock files
    img_resized = ImageOps.fit(img, (100, 100))
    img_buffer = BytesIO()
    img_resized.save(img_buffer, format="PNG")
    img_data = (f"result_{task_id}.png", "image/png", img_buffer.getvalue())

    json_data = (f"result_{task_id}.json", "application/json",
                 f'{{"task_id": "{task_id}", "width": {img.width}, "height": {img.height}}}'.encode())
    files = [img_data, json_data]

    result = {"processed": True, "task_id": task_id}
    dummy_tasks[task_id] = TaskResult(status=TaskStatus.COMPLETED, result=result, files=files)


# Mock async check function
async def check(task_id: str) -> TaskResult:
    return dummy_tasks.get(task_id, TaskResult(status=TaskStatus.FAILED))


# Gradio interface setup
def create_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Asynchronous Task Interface")
        image_input = gr.Image(type="pil", label="Upload Image")
        submit_btn = gr.Button("Submit Task", variant="primary")

        # Outputs: status, result JSON, 10 download buttons, 10 image blocks
        status_out = gr.Textbox(label="Status", interactive=False, visible=True)
        result_out = gr.JSON(label="Result", visible=True)
        download_btns = [gr.DownloadButton(label=f"Download File {i + 1}", visible=False) for i in range(10)]
        img_blocks = [gr.Image(label=f"Generated Image {i + 1}", visible=False) for i in range(10)]

        # Event handler for submit button
        async def submit_handler(img):
            if not img:
                return ("No image provided", None) + [gr.update(visible=False)] * 20

            task_id = await queue_task(img)
            while True:
                task_result = await check(task_id)
                if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    break
                await asyncio.sleep(1)

            status = task_result.status.value.capitalize()
            result = task_result.result

            # Handle files
            downloads_to_show = []
            images_to_show = []
            if task_result.files:
                for filename, ftype, fdata in task_result.files:
                    with BytesIO(fdata) as f_buffer:
                        # Save to tmp file for serving
                        tmp_path = f"/tmp/{filename}"  # Adjust path as needed; ensure directory exists
                        with open(tmp_path, "wb") as tmp_file:
                            tmp_file.write(f_buffer.getvalue())
                        downloads_to_show.append(tmp_path)
                        if "image" in ftype.lower():
                            images_to_show.append(tmp_path)

            print(images_to_show, downloads_to_show)
            # Prepare updates for download buttons and image blocks
            download_updates = ([gr.update(value=p, visible=True, label=f"Download {p.split('/')[-1]}") for p in
                                 downloads_to_show] +
                                [gr.update(visible=False)] * (10 - len(downloads_to_show)))
            image_updates = ([gr.update(value=p, visible=True) for p in images_to_show] +
                             [gr.update(visible=False)] * (10 - len(images_to_show)))

            # Return updates: status, result, downloads[0-9], images[0-9]
            return (status, result) + tuple(download_updates + image_updates)

        submit_btn.click(
            submit_handler,
            inputs=image_input,
            outputs=[status_out, result_out] + download_btns + img_blocks
        )

    return demo


# Launch the interface
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()