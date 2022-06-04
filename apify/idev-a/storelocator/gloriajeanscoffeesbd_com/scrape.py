from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gloriajeanscoffeesbd")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://gloriajeanscoffeesbd.com/"
base_url = "https://gloriajeanscoffeesbd.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select('div[data-elementor-type="footer"] ul')[-1].select("li")
        for _ in locations:
            block = list(_.stripped_strings)
            addr = block[1].replace(".", ",").split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=block[0].replace(":", "").strip(),
                street_address=", ".join(addr[:-1]),
                city=addr[-1].split()[0].split("-")[0].strip(),
                zip_postal=addr[-1].split()[-1].split("-")[-1].strip(),
                country_code="Bangladesh",
                locator_domain=locator_domain,
                raw_address=block[1],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
