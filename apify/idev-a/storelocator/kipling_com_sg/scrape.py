from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.sg"
base_url = "https://www.kipling.com.sg/kipling-stores/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("li.address-item")
        for _ in locations:
            raw_address = _.select_one("div.address").text.strip()
            addr = raw_address.split(",")
            zip_postal = addr[-1].strip().split()[-1]
            if not zip_postal.isdigit():
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-id"],
                location_name=_.select_one("div.name").text.strip(),
                street_address=", ".join(addr[:-1]),
                city=addr[-1].strip().split()[0].replace("Level", ""),
                zip_postal=zip_postal,
                country_code="SG",
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
