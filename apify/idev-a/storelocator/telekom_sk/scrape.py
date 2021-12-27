from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.telekom.sk"
base_url = "https://backvm.telekom.sk/www/predajne/?requestSource=js"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = []
            for hh in bs(_["Open"], "lxml").stripped_strings:
                if "PREDAJŇA" in hh:
                    break
                for hr in hh.split("\n"):
                    if "HAJNIKOVAH" in hr:
                        break
                    hours.append(hr)
            yield SgRecord(
                page_url="https://www.telekom.sk/predajne",
                store_number=_["ID"],
                location_name=_["Name"],
                street_address=_["Street"],
                city=_["City"],
                zip_postal=_["ZIP"],
                latitude=_["LatLng"].split(",")[0].strip(),
                longitude=_["LatLng"].split(",")[1].strip(),
                country_code="Slovakia",
                phone=_["Phone"].split(":")[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
