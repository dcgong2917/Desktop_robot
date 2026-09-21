from PyQt6.QtCore import QThread, pyqtSignal


class AsyncWorker(QThread):
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    chunk_received = pyqtSignal(str)  # 流式回复用

    def __init__(self, fn, *args, stream=False, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._stream = stream

    def run(self):
        try:
            if self._stream:
                for chunk in self._fn(*self._args, **self._kwargs):
                    self.chunk_received.emit(chunk)
                self.result_ready.emit(None)
            else:
                result = self._fn(*self._args, **self._kwargs)
                self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
