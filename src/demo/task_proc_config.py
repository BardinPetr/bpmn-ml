from ray.serve.schema import TaskProcessorConfig, CeleryAdapterConfig

TASK_PROCESSOR_CONFIG = TaskProcessorConfig(
    queue_name="my_queue",
    adapter="ray.serve.task_processor.CeleryTaskProcessorAdapter",
    adapter_config=CeleryAdapterConfig(
        broker_url="redis://localhost:16379/0",
        backend_url="redis://localhost:16379/1",
    ),
    max_retries=5,
    failed_task_queue_name="failed_tasks"
)
