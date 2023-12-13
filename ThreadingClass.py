import threading
import time
import logging

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| => %(message)s")


class WorkerSignals:
    canceled = threading.Event()


class WorkerThread(threading.Thread, ):
    def __init__(self, seconds, signals, main_window):
        super().__init__()
        self.seconds = seconds
        self.signals = signals
        self.main_window = main_window
        # Initialize progress value
        self.progress_value = 0

    def run(self):
        for i in range(self.seconds):
            time.sleep(1)
            self.update_progress()
            if self.signals.canceled.is_set():
                print(
                    f'Thread canceled - Remaining time: {self.seconds - i - 1} seconds')
                logging.info(
                    f'Thread canceled - Remaining time: {self.seconds - i - 1} seconds')
                return
        print('Thread completed')
        logging.info('Thread completed')

    def cancel(self):
        self.signals.canceled.set()
        self.join()

    def update_progress(self):
        # This function can be called to update the progress bar manually
        self.progress_value += 20
        self.main_window.ui.progressBar.setValue(self.progress_value)



        logging.info("Mixing completed.")
