from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizzatwist")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pizzatwist.com/"
base_url = "https://pizzatwist.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main_popular div.p_card div.col-lg-6.col-md-6")
        for _ in locations:
            if "Coming Soon" in _.select_one("a.card_btn").text:
                continue
            addr = [aa.text.strip() for aa in _.select("p")]
            _city = " ".join(
                [
                    cc.strip()
                    for cc in addr[-1].replace(",", " ").split(" ")
                    if cc.strip()
                ]
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=" ".join(_city.split(" ")[:-2]),
                state=_city.split(" ")[-2].strip(),
                zip_postal=_city.split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
