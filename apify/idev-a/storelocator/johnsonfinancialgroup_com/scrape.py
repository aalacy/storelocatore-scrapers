from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("johnsonfinancialgroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.johnsonfinancialgroup.com"
base_url = "https://johnsonbank.locatorsearch.com/GetItems.aspx"


def fetch_data():
    with SgRequests() as session:
        data = {
            "lat": "42.89130379703694",
            "lng": "-88.55598999999998",
            "searchby": "FCS|DRIVEUP|",
            "SearchKey": "",
            "rnd": "1628616152564",
        }
        soup = bs(
            session.post(base_url, headers=_headers, data=data)
            .text.replace("<![CDATA[", "")
            .replace("]]>", ""),
            "lxml",
        )
        locations = soup.select("marker")
        for _ in locations:
            addr = list(_.add2.stripped_strings)
            hours = [
                " ".join(hh.stripped_strings)
                for hh in _.select("table")[0].select("tr")
            ]
            yield SgRecord(
                page_url=base_url,
                location_name=_.title.text.strip(),
                street_address=_.add1.text.strip(),
                city=addr[0].split(",")[0].strip(),
                state=addr[0].split(",")[1].strip().split(" ")[0],
                zip_postal=" ".join(addr[0].split(",")[1].strip().split(" ")[1:]),
                country_code="US",
                phone=addr[-1],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
