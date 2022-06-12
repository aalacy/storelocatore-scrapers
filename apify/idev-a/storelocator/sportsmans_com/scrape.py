from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sportsmans")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sportsmans.com"
base_url = "https://www.sportsmans.com/store-locator?q=90045&page={}"


def fetch_data():
    with SgRequests() as session:
        page = 0
        while True:
            try:
                locations = session.get(base_url.format(page), headers=_headers).json()[
                    "data"
                ]
            except:
                break
            page += 1
            for _ in locations:
                location_name = f"{_['warehouseNameStart']} {_['displayName']} {_['warehouseNameEnd']} {_['name']}"
                street_address = _["line1"]
                if _["line2"]:
                    street_address += " " + _["line2"]
                page_url = _["url"]
                logger.info(page_url)
                hours = []
                if not page_url and _["town"] == "Pittsburgh":
                    page_url = "https://stores.sportsmans.com/sportsmans-warehouse/us/pa/pittsburgh/120-quinn-drive"
                if page_url:
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    for hh in sp1.select("table.c-location-hours-details tbody tr"):
                        td = hh.select("td")
                        hours.append(
                            f"{td[0].text.strip()}: {' '.join(td[1].stripped_strings)}"
                        )
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["name"],
                    location_name=location_name,
                    street_address=street_address,
                    city=_["town"],
                    state=_["state"],
                    zip_postal=_["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="US",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
