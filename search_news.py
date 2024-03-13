import argparse
import json
import logging
import os
import pprint
from typing import Dict, List

import requests
from dotenv import load_dotenv

import config

# Add the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")

load_dotenv(dotenv_path)

# Get the API key from the environment variable
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")

# Get the API URL from the config file
NEWS_SEARCH_URL = config.NEWS_SEARCH_URL

pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(level=config.LOGGING_LEVEL)


def search_news(
    search_term: str, page: int = 1
) -> List[Dict]:
    url = NEWS_SEARCH_URL
    querystring = {
        "query": search_term,
        "page": page
    }
    headers = {
        "X-RapidAPI-Key": str(RAPID_API_KEY),
        "X-RapidAPI-Host": config.JOB_SEARCH_X_RAPIDAPI_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        json_object = json.loads(response.text)
        json_response_data = json_object.get("data")
        return json_response_data
    except ValueError as value_err:
        logging.error(value_err)
        return [{"error": value_err}]


def main(search_term, page):
    results = search_news(
        search_term=search_term, page=page
    )
    return results


def entrypoint():
    parser = argparse.ArgumentParser(description="This searches for news")

    parser.add_argument(
        "search",
        type=str,
        metavar="search"
        help="the term to search for",
    )

    parser.add_argument(
        "page",
        type=int,
        default=1,
        metavar="page",
        help="the page of results, page 1, 2, 3,...etc.",
    )

    args = parser.parse_args()

    result = main(
        search_term=args.search, page=args.page
    )

    pp.pprint(result)


if __name__ == "__main__":
    entrypoint()
