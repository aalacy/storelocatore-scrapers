from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("watrust")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://watrust.com"
base_url = "https://watrust.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.location-data")
        for _ in locations:
            name = _["data-title"]
            addr = _["data-address"].split(",")
            location_type = ""
            if "ATM" in name:
                location_type = "ATM"
            page_url = locator_domain + _["data-link"]
            coord = _["data-coords"][1:-1].split()
            if not coord:
                coord = ["", ""]
            hours_of_operation = _.get("data-lobbyhours")
            if hours_of_operation:
                hours_of_operation = hours_of_operation[1:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=name,
                street_address=" ".join(addr[:-2]),
                city=addr[-2],
                state=addr[-1].strip().split()[0],
                zip_postal=addr[-1].strip().split()[-1],
                country_code="US",
                phone=_.get("data-phonenumberlink"),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
                raw_address=_["data-address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
