from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("interlinksupply")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://interlinksupply.com/"
    base_url = "https://interlinksupply.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.mapListingContainer div.col-25-percent")
        for _ in locations:
            block = list(_.stripped_strings)
            location_name = block[0]
            phone = ""
            del block[0]
            if "Aramsco" in block[0]:
                del block[0]
            if "Toll" in block[-1]:
                del block[-1]
            if "Ph" in block[-1]:
                phone = block[-1].split(":")[-1]
                del block[-1]

            addr = block
            zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
            if not zip_postal.replace("-", "").isdigit():
                zip_postal = addr[-1].split(",")[-1]
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(block),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
