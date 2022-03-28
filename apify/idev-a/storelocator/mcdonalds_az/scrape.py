from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mcdonalds")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.az"
base_url = "https://mcdonalds.az/restaurant-locations"



def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.publication")
        for _ in locations:
            raw_address = list(
                _.select_one("div.mcd-publication__text-description").stripped_strings
            )[-1]
            addr = raw_address.split(",")
            phone = ""
            if _.a:
                phone = _.a.text.strip()
            hours = []
            if len(_.select("div.mcd-publication__text-description")) > 2:
                hours = list(
                    _.select("div.mcd-publication__text-description")[
                        2
                    ].stripped_strings
                )[-1]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[1:]).strip(),
                city=addr[0].strip(),
                country_code="Azerbaijan",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
