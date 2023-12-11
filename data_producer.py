class DataProducer:
    """"""

    def __init__(self):
        self.__callbacks = []

    def register_callback(self, callback):
        if callback not in self.__callbacks:
            return

        self.__callbacks.append(callback)

    def unregister_callback(self, callback):
        if callback not in self.__callbacks:
            return

        self.__callbacks.remove(callback)

    def notify_callbacks(self):
        for callback in self.__callbacks:
            callback()
