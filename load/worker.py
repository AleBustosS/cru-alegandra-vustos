from PyQt5.QtCore import QObject, pyqtSignal, QRunnable


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    """Worker que ejecuta una función en un hilo separado y emite señales.

    Uso: 
        worker = Worker(func, *args, **kwargs)
        worker.signals.result.connect(slot_result)
        QThreadPool.globalInstance().start(worker)
    """
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))
        else:
            self.signals.result.emit(res)
        finally:
            self.signals.finished.emit()
