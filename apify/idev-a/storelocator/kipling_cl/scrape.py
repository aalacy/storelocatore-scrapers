from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.cl"
base_url = "https://www.kipling.cl/tiendas-kipling/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        names = [
            hh.text.strip()
            for hh in soup.select("div.container div.container-two div.tiendas h3")
        ]
        addresses = [
            hh.text.strip()
            for hh in soup.select("div.container div.container-two div.direccion h3")
        ]
        hr = [
            hh.text.strip()
            for hh in soup.select("div.container div.container-two div.horario h3")
        ]
        for x in range(len(names)):
            raw_address = "Av " + addresses[x].split("Av")[-1].replace(".", "")
            yield SgRecord(
                page_url=base_url,
                location_name="Kipling",
                street_address=raw_address,
                country_code="Chile",
                locator_domain=locator_domain,
                raw_address=addresses[x],
                hours_of_operation=hr[x],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
