from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import time
import json

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://www.needlersfreshmarket.com/"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    base_url = "https://api.freshop.com/1/stores?app_key=needle&has_address=true&limit=-1&token="
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url.startswith(base_url) and rr.response:
                    exist = True
                    locations = json.loads(rr.response.body)["items"]
                    for _ in locations:
                        country = "US"
                        if len(_["postal_code"]) > 5:
                            country = "CA"

                        yield SgRecord(
                            page_url=_["url"],
                            store_number=_["store_number"],
                            location_name=_["name"],
                            street_address=_["address_1"],
                            city=_["city"],
                            state=_["state"],
                            zip_postal=_["postal_code"],
                            country_code=country,
                            phone=_["phone"].split("\n")[0],
                            latitude=_["latitude"],
                            longitude=_["longitude"],
                            locator_domain=locator_domain,
                            hours_of_operation=_["hours_md"]
                            .split("\n")[0]
                            .replace("Open", ""),
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
