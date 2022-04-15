from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.cl"
base_url = "https://www.thenorthface.cl/tiendas"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store-card")
        for _ in locations:
            p = _.select("p")
            coord = p[3].a["href"].split("/@")[1].split("/data")[0].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=p[0].text.strip(),
                street_address=p[1].text.strip(),
                country_code="CL",
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=p[2].text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
