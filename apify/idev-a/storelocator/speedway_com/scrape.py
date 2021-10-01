from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("speedway")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.speedway.com"
base_url = "https://www.speedway.com/locations/search"


def fetch_data():
    with SgRequests() as session:
        data = {
            "SearchType": "search",
            "SearchText": "",
            "StartIndex": "0",
            "Limit": "100000",
            "Latitude": "37.09024",
            "Longitude": "-95.712891",
            "Radius": "1000000",
            "Filters[FuelType]": "Unleaded",
            "Filters[OnlyFavorites]": "false",
            "Filters[Text]": "",
        }
        soup = bs(session.post(base_url, headers=_headers, data=data).text, "lxml")
        locations = soup.select("section.c-location-card")
        for _ in locations:
            coming_soon = _.select_one("p.c-bottom-status-text")
            if coming_soon and coming_soon.text.strip() == "Coming Soon":
                continue
            addr = (
                _.select_one('li[data-location-details="address"]')
                .text.strip()
                .split(",")
            )
            phone = ""
            if _.select_one('li[data-location-details="phone"]'):
                phone = _.select_one('li[data-location-details="phone"]').text.strip()
            page_url = (
                locator_domain
                + _.select_one("div.c-location-heading__primary a")["href"]
            )
            _hr = _.select_one("ul.c-location-options__list span.icon-24-hour-store")
            hours_of_operation = ""
            if _hr:
                hours_of_operation = _hr.find_next_sibling().text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["data-costcenter"],
                location_name=_["data-storename"],
                street_address=_.select_one(
                    "div.c-location-heading__primary a"
                ).text.strip(),
                city=addr[0].strip(),
                state=_["data-state"],
                zip_postal=addr[-1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
