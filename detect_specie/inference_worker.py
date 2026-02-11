import threading


class InferenceWorker(threading.Thread):
    def __init__(self, model_service, image_path, lat, lon, queue, class_mapping, transform):
        super().__init__(daemon=True)
        self.model_service = model_service
        self.image_path = image_path
        self.lat = lat
        self.lon = lon
        self.queue = queue
        self.class_mapping = class_mapping
        self.transform = transform

    def run(self):
        try:
            from detect_specie.main import find_specie

            specie = find_specie(
                self.image_path,
                self.lat,
                self.lon,
                self.model_service.net,
                self.class_mapping,
                self.transform
            )

            self.queue.put(("inference_done", (specie, self.image_path)))

        except Exception as e:
            self.queue.put(("inference_error", str(e)))
