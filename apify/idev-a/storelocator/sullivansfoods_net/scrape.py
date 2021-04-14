from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sullivansfoods_net")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "referer": "https://www.sullivansfoods.net/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def _hour(_):
    return _valid(_["hours_md"].split("\n")[0].replace("Store Hours:", "").strip())


def fetch_data():
    locator_domain = "https://www.sullivansfoods.net"
    base_url = "https://www.sullivansfoods.net/my-store/store-locator"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if (
                    rr.url.startswith("https://api.freshop.com/1/stores?app_key")
                    and rr.response
                ):
                    exist = True
                    url = f'https://api.freshop.com/1/stores?app_key=sullivans&has_address=true&limit=-1&token={rr.url.split("token=")[1]}'
                    with SgRequests() as session:
                        locations = session.get(url, headers=_headers).json()["items"]
                        logger.info(f"{len(locations)} locations found")
                        for _ in locations:
                            yield SgRecord(
                                store_number=_["store_number"],
                                page_url=_["url"],
                                location_name=_["name"],
                                street_address=f"{_['address_1']} {_.get('address_2', '')}",
                                city=_["city"],
                                state=_["state"],
                                zip_postal=_["postal_code"],
                                country_code="US",
                                phone=_["phone"].split("\n")[0].strip(),
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                locator_domain=locator_domain,
                                hours_of_operation=_hour(_),
                            )

                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
