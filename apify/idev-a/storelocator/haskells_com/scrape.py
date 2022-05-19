from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("haskells")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.haskells.com/"
base_url = "https://haskells.irishtitan.cloud/locations"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=_["streetAddress"],
                city=_["addressLocality"].split(",")[0].strip(),
                state=_["addressLocality"].split(",")[1].strip(),
                zip_postal=_["postalCode"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                hours_of_operation="; ".join(
                    bs(_["hours"], "lxml").stripped_strings
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
