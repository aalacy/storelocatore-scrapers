from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.cafishgrill.com/"
base_url = "https://www.cafishgrill.com/pages/stores-json"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        scripts = json.loads(soup.find("script", id="StoreJSON").string)["stores"]
        for _ in scripts:
            addr = parse_address_intl(_["Locality"])
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            temp = list(bs(_["Street_add"], "lxml").stripped_strings)
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]}: {temp[x+1]}")

            if "COMING SOON" in _["Fax_number"]:
                continue

            yield SgRecord(
                page_url="https://www.cafishgrill.com/pages/locations",
                store_number=_["uuid"],
                location_name=_["Fcilty_nam"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["Ycoord"],
                longitude=_["Xcoord"],
                country_code="US",
                phone=_["Phone_number"].split(":")[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["Locality"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
