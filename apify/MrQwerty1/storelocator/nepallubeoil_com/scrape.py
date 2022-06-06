from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[@id='tablepress-1']/tbody/tr")

    for d in divs:
        store_number = "".join(d.xpath("./td[1]/text()")).strip()
        location_name = "".join(d.xpath("./td[2]/text()")).strip()
        city = "".join(d.xpath("./td[3]/text()")).strip()
        phone = "".join(d.xpath("./td[5]/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            city=city,
            phone=phone,
            country_code="NP",
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://nepallubeoil.com/"
    page_url = "http://nepallubeoil.com/contact-us/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
