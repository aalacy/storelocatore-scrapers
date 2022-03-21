from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("razzoos")

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "client_type": "web",
    "referer": "https://www.razzoos.com/locations/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.razzoos.com"
base_url = "https://www.razzoos.com/locations/"
api_url = "https://www.razzoos.com/api"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        links = soup.select("div.location-accordian")
        logger.info(f"{len(links)} found")
        for link in links:
            store_number = link["data-loc"].split("-")[-1]
            _headers["path"] = f"locations/{store_number}"
            logger.info(store_number)
            _ = session.get(api_url, headers=_headers).json()
            page_url = base_url + _["path"]
            hours = []
            for hh in _.get("hours", []):
                hours.append(f"{hh['day']}: {hh['open']} - {hh['close']}")
            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
