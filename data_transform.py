import concurrent.futures
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from config import LOGGING_LEVEL, RAW_DATA_PATH, PROCESSED_DATA_PATH
from file_handler import FileHandler

logging.basicConfig(level=LOGGING_LEVEL)


class DataTransformer:
    """Transforms the raw data into a format that is ready for analysis."""

    def __init__(
        self, raw_path: str, processed_path: str, data: List[dict]
    ):
        self.data = data
        self.file_handler = FileHandler(
            raw_path=raw_path, processed_path=processed_path
        )

    def concatenate_videos(self):
        for item in self.data:
            if "videos" in item:
                videos = item["videos"]
                if videos:
                    item["videos"] = "\n".join(videos)
                else:
                    item["videos"] = ""

    def add_source_and_remove_publisher(self):
        for item in self.data:
            if "publisher" in item:
                item["source"] = item["publisher"]["title"]

    def extract_date_only(self):
        for item in self.data:
            if "date" in item:
                date_string = item["date"]
                parsed_date = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")
                formatted_date = parsed_date.strftime("%Y-%m-%d")
                item["date"] = formatted_date
    
    def delete_json_keys(self, *keys):
        """Deletes the specified keys from the json data."""
        for item in self.data:
            for key in keys:
                if key in item:
                    del item[key]

    def drop_variables(self):
        """Drops the variables that are not needed for analysis."""
        self.delete_json_keys(
            "publisher",
            "images"
        )

    def transform(self):
        """Transforms the raw data into a format that is ready for analysis."""

        self.concatenate_videos()
        self.add_source_and_remove_publisher()
        self.extract_date_only()
        self.drop_variables()

        self.file_handler.save_data_list(
            data_list=self.data,
            source="news",
            sink=self.file_handler.processed_path,
        )


class Main:
    def __init__(self):
        self.file_handler = FileHandler(
            raw_path=RAW_DATA_PATH, processed_path=PROCESSED_DATA_PATH
        )
        self.data = self.file_handler.import_news_data_from_dir(
            dirpath=RAW_DATA_PATH
        )

        self.transformer = DataTransformer(
            raw_path=str(RAW_DATA_PATH),
            processed_path=str(PROCESSED_DATA_PATH),
            data=self.data,
        )

    def run(self):
        self.transformer.transform()


if __name__ == "__main__":
    main = Main()
    main.run()
