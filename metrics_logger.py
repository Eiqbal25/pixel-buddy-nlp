import csv
import time
import os
from datetime import datetime

class MetricsLogger:
    def __init__(self, filename="experiment_metrics.csv"):
        self.filename = filename

        # Create file with header if not exists
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "input_type",        # voice / text / quick
                    "query_length",
                    "stt_time",
                    "nlp_time",
                    "tts_time",
                    "total_response_time",
                    "tts_success"
                ])

    def log(
        self,
        input_type,
        query_length,
        stt_time,
        nlp_time,
        tts_time,
        total_time,
        tts_success
    ):
        with open(self.filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                input_type,
                query_length,
                round(stt_time, 3),
                round(nlp_time, 3),
                round(tts_time, 3),
                round(total_time, 3),
                tts_success
            ])
