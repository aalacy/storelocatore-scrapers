from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mamasandpapas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mamasandpapas.com"
base_url = "https://cdn.shopify.com/s/files/1/0414/6023/6453/t/1/assets/sca.storelocatordata.json?v=1630403613&formattedAddress=&boundsNorthEast=&boundsSouthWest=&_=1631007103630"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if _["tagsvalue"] != "Store":
                continue
            hours = []
            if _["schedule"]:
                hours = bs(_["schedule"], "lxml").stripped_strings
            for hh in _.get("OpenHours", []):
                hours.append(f"{hh['DayName']}: {hh['From']} - {hh['To']}")
            street_address = _["address"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            page_url = _.get("web")
            if not page_url:
                page_url = f"https://www.mamasandpapas.com/pages/{_['name'].lower().replace(',','').replace(' ','-')}"
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                raw_address = list(
                    sp1.select_one("div.storeloc-details-address").stripped_strings
                )[1:-1]
                addr = parse_address_intl(", ".join(raw_address))
                city = addr.city
                state = addr.state
            else:
                city = _.get("city")
                state = _.get("state")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=_.get("postal"),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=_.get("phone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=", ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
