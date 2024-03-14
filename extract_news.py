import config
import logging
import os
import concurrent.futures
from dotenv import load_dotenv
from file_handler import FileHandler
from search_news import search_news


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THIS_DIR)

file_handler = FileHandler(
    raw_path=config.RAW_DATA_PATH, processed_path=config.PROCESSED_DATA_PATH
)

# Load the .env file
load_dotenv("../../.env")

# Get the API key from the environment variable
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")

def get_all_news(search_term, pages, start_date, end_date):
    all_news = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for page in range(0, pages):
            futures.append(
                executor.submit(
                    search_news,
                    search_term=search_term,
                    from_date = start_date,
                    to_date = end_date,
                    page=page,
                )
            )
        for future in concurrent.futures.as_completed(futures):
            try:
                news = future.result()
                if news:
                    all_news.extend(news)
                    logging.debug("Appended %d news for page %d", len(news), page)
                    for news in all_news:
                        file_handler.save_data(
                            data=news,
                            source="news",
                            sink=file_handler.raw_path,
                        )
                else:
                    logging.warning("No news found for page %d", page)
            except Exception as e:
                logging.error(
                    "An error occurred while fetching news for page %d: %s",
                    page,
                    str(e),
                )
    print(len(all_news))
    return all_news


def extract(news_search, start_date, end_date):
    """
    This function extracts data from the News API and saves it locally.
    """
    file_handler.create_data_folders_if_not_exists()
    try:
        logging.info(
            "Starting extraction process for News Search: %s",
            news_search,
        )
        get_all_news(
            search_term=news_search,
            start_date = start_date,
            end_date = end_date,
            pages=config.PAGES,
        )

        logging.info("Extraction process completed for News Search: %s", news_search)

    except Exception as e:
        logging.error("An error occurred in the extract function: %s", str(e))

if __name__ == "__main__":
    logging.info("Application started.")
    extract('TSLA', '01/01/2023', '01/01/2024')
    logging.info("Application finished.")