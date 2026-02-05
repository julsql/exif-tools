class ModelService:
    def __init__(self):
        self.net = None
        self.model_info = None
        self.ready = False
        self.loading = False
        self.error = None

    def is_ready(self):
        return self.ready and self.net is not None

    def set_error(self, error):
        self.error = error
        self.ready = False
        self.loading = False
