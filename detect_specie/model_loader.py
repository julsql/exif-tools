import threading
from pathlib import Path

MODEL_PATH = Path.home() / ".exiftools" / "models" / "vit_reg4_m16_rms_avg_i-jepa-inat21.pt"


class ModelLoaderThread(threading.Thread):
    def __init__(self, model_service, queue):
        super().__init__(daemon=True)
        self.model_service = model_service
        self.queue = queue

    def run(self):
        try:
            self.model_service.loading = True

            import birder

            net, model_info = birder.load_pretrained_model(
                "vit_reg4_m16_rms_avg_i-jepa-inat21",
                inference=True,
                dst=MODEL_PATH
            )

            self.model_service.net = net
            self.model_service.model_info = model_info
            self.model_service.ready = True
            self.model_service.loading = False

            self.queue.put(("model_ready", None))

        except Exception as e:
            self.model_service.set_error(str(e))
            self.queue.put(("model_error", str(e)))
