#!/.venv/bin/python

import argparse
import logging
import requests
import time
from datetime import datetime

TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"
MONTH_FMT = "%Y-%m"

LEGACY = "legacy"
V0 = "v0"


def main(args):
    logger = logging.getLogger(__name__)
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    logger.info("Triggering save event...")
    before = datetime.utcnow()
    trigger_response = requests.post(args.log_api)
    players = trigger_response.json()
    logger.info(f"Triggered save for players {players}")

    logger.info("Sleeping 20 seconds...")
    time.sleep(20.0)
    after = datetime.utcnow()

    for player in players:
        start_time = datetime.strftime(before, TIMESTAMP_FMT)
        end_time = datetime.strftime(after, TIMESTAMP_FMT)
        logger.info(
            f"Querying granular data for {player}, "
            f"startTime={start_time}, endTime={end_time}"
        )
        query_response = requests.get(
            args.query_api + V0,
            params=dict(
                player=player,
                startTime=start_time,
                endTime=end_time,
            ),
        )
        granular_result = query_response.json()
        if query_response.status_code != 200 or not granular_result:
            logger.error(f"Received unexpected response: {granular_result}")
            raise AssertionError(f"Granular query for player {player} invalid.")

        start_time = datetime.strftime(before, DATE_FMT)
        end_time = datetime.strftime(after, DATE_FMT)
        logger.info(
            f"Querying daily aggregated data for {player}, "
            f"startTime={start_time}, endTime={end_time}"
        )
        query_response = requests.get(
            args.query_api + V0,
            params=dict(
                player=player,
                startTime=start_time,
                endTime=end_time,
            ),
        )
        daily_result = query_response.json()
        if query_response.status_code != 200 or not daily_result:
            logger.error(f"Received unexpected response: {daily_result}")
            raise AssertionError(f"Daily aggregated query for player {player} invalid.")

        for category in ["level", "rank", "experience"]:
            sql = (
                f"SELECT timestamp,Slayer,Farming FROM skills.{category} "
                f"WHERE player='{player}' AND timestamp > '{start_time} 00:00:00' "
                f"AND timestamp < '{end_time} 23:59:59' ORDER BY timestamp ASC"
            )
            logger.info(f"Querying legacy API for sql={sql}")
            query_response = requests.get(args.query_api + LEGACY, params=dict(sql=sql))
            legacy_result = query_response.json()
            if query_response.status_code != 200 or not legacy_result:
                logger.error(f"Received unexpected response: {legacy_result}")
                raise AssertionError(
                    f"Daily aggregated query for player {player} invalid."
                )

        start_time = datetime.strftime(before, MONTH_FMT)
        end_time = datetime.strftime(after, MONTH_FMT)
        logger.info(
            f"Querying monthly aggregated data for {player}, "
            f"startTime={start_time}, endTime={end_time}"
        )
        query_response = requests.get(
            args.query_api + V0,
            params=dict(
                player=player,
                startTime=start_time,
                endTime=end_time,
            ),
        )
        monthly_result = query_response.json()
        if query_response.status_code != 200 or not monthly_result:
            logger.error(f"Received unexpected response: {monthly_result}")
            raise AssertionError(
                f"Monthly aggregated query for player {player} invalid."
            )

    logger.info("TESTS PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--log-api",
        type=str,
        help="Endpoint to trigger a log event.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--query-api",
        type=str,
        help="Endpoint to query database.",
        required=True,
    )
    args = parser.parse_args()

    main(args)
