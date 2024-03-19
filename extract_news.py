import config
import logging
import os
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from file_handler import FileHandler
from search_news import search_news


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THIS_DIR)

file_handler = FileHandler(
    raw_path=config.RAW_DATA_PATH, processed_path=config.PROCESSED_DATA_PATH
)

# Load the .env file
load_dotenv(".env")

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
                    from_date=start_date,
                    to_date=end_date,
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


# def extract(news_search, start_date, end_date):
#     """
#     This function extracts data from the News API and saves it locally.
#     """
#     file_handler.create_data_folders_if_not_exists()
#     try:
#         logging.info(
#             "Starting extraction process for News Search: %s",
#             news_search,
#         )
#         get_all_news(
#             search_term=news_search,
#             start_date = start_date,
#             end_date = end_date,
#             pages=config.PAGES,
#         )

#         logging.info("Extraction process completed for News Search: %s", news_search)

#     except Exception as e:
#         logging.error("An error occurred in the extract function: %s", str(e))

def extract(news_search, start_date_str, end_date_str):
    """
    This function extracts data from the News API and saves it locally.
    """
    file_handler.create_data_folders_if_not_exists()
    try:
        logging.info(
            "Starting extraction process for News Search: %s",
            news_search,
        )
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

        current_date = start_date
        num_threads = 10
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            while current_date <= end_date:
                next_year = current_date.replace(
                    year=current_date.year + 1, day=1, month=1
                )
                min_end_date = min(next_year, end_date)
                future = executor.submit(
                    get_all_news,
                    search_term=news_search,
                    start_date=current_date.strftime("%d/%m/%Y"),
                    end_date=min_end_date.strftime("%d/%m/%Y"),
                    pages=config.PAGES,
                )
                futures.append(future)  # Move this line inside the loop
                current_date = next_year

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                # Process the result if necessary
            except Exception as e:
                logging.error(f"An error occurred: {e}")

        logging.info("Extraction process completed for News Search: %s", news_search)
    except Exception as ex:
        logging.error(f"An error occurred during extraction: {ex}")


if __name__ == "__main__":
    logging.info("Application started.")
    extract("Federal Reserve", "01/01/2024", "01/03/2024")
    logging.info("Application finished.")
