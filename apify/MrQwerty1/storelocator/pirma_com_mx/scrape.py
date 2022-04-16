from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table//tr")
    divs.pop(0)

    for d in divs:
        store_number = "".join(d.xpath("./td[1]/text()")).strip()
        location_name = "".join(d.xpath("./td[2]/text()")).strip()
        street_address = "".join(d.xpath("./td[3]/text()")).strip()
        city = "".join(d.xpath("./td[4]/text()")).strip()
        postal = "".join(d.xpath("./td[5]/text()")).strip()
        phone = "".join(d.xpath("./td[6]/text()")).strip()
        state = "".join(d.xpath("./td[8]/text()")).strip()
        latitude = "".join(d.xpath("./td[9]/text()")).strip()
        longitude = "".join(d.xpath("./td[10]/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MX",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://pirma.com.mx/"
    page_url = "https://pirma.com.mx/pages/tiendas-fisicas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
