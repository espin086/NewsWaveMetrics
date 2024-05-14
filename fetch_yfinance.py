import argparse
import yfinance as yf


def fetch_info(ticker):
    stock = yf.Ticker(ticker)
    return stock.info


def fetch_history(ticker, interval="1d"):
    stock = yf.Ticker(ticker)
    return stock.history(interval=interval)


def fetch_actions(ticker):
    stock = yf.Ticker(ticker)
    return stock.actions


def fetch_financials(ticker):
    stock = yf.Ticker(ticker)
    return {
        "income_statement": stock.income_stmt,
        "quarterly_income_statement": stock.quarterly_income_stmt,
        "balance_sheet": stock.balance_sheet,
        "quarterly_balance_sheet": stock.quarterly_balance_sheet,
        "cash_flow": stock.cashflow,
        "quarterly_cash_flow": stock.quarterly_cashflow,
    }


def fetch_holders(ticker):
    stock = yf.Ticker(ticker)
    return {
        "major_holders": stock.major_holders,
        "institutional_holders": stock.institutional_holders,
        "mutualfund_holders": stock.mutualfund_holders,
    }


def fetch_recommendations(ticker):
    stock = yf.Ticker(ticker)
    return {
        "recommendations_summary": stock.recommendations_summary,
        "recommendations": stock.recommendations,
    }


def setup_argparse():
    parser = argparse.ArgumentParser(description="Fetch stock data from Yahoo Finance.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol.")
    parser.add_argument(
        "--data_type",
        choices=[
            "info",
            "history",
            "actions",
            "financials",
            "holders",
            "recommendations",
        ],
        help="Type of data to fetch.",
    )
    return parser.parse_args()


def main():
    args = setup_argparse()
    functions = {
        "info": fetch_info,
        "history": fetch_history,
        "actions": fetch_actions,
        "financials": fetch_financials,
        "holders": fetch_holders,
        "recommendations": fetch_recommendations,
    }
    if args.data_type in functions:
        result = functions[args.data_type](args.ticker)
        print(result)


if __name__ == "__main__":
    main()
