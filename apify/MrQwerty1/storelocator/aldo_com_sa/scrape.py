from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://aldo.com.sa/apps/store-locator"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(
        tree.xpath("//script[contains(text(), 'markersCoords.push(')]/text()")
    )
    divs = tree.xpath("//a[./span[@class='name']]")
    for d in divs:
        location_name = "".join(d.xpath("./span[@class='name']/text()")).strip()
        street_address = "".join(d.xpath("./span[@class='address']/text()")).strip()
        city = "".join(d.xpath("./span[@class='city']/text()")).strip()
        state = SgRecord.MISSING
        postal = "".join(d.xpath("./span[@class='postal_zip']/text()")).strip()

        store_number = "".join(d.xpath("./@onclick")).split("popup(")[1].split(",")[0]
        try:
            latitude = (
                text.split(store_number)[0].split("lat:")[-1].split(",")[0].strip()
            )
            longitude = (
                text.split(store_number)[0].split("lng:")[-1].split(",")[0].strip()
            )
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="SA",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://aldo.com.sa/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
