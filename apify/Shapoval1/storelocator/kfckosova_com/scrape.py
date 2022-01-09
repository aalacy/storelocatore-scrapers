from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfckosova.com/"
    api_url = "https://kfckosova.com/restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="map-list-holder__item"]')
    for d in div:

        page_url = "https://kfckosova.com/restaurants/"
        location_name = "".join(d.xpath(".//h3/text()"))
        street_address = "<MISSING>"
        country_code = "Kosovo"
        city = "".join(d.xpath(".//h3/following-sibling::h5/text()")) or "<MISSING>"
        if location_name.find("Qendra Tregtare Albi Mall, Kati 3-të, Pristina") != -1:
            city = "Pristina"
            street_address = "Qendra Tregtare Albi Mall, Kati 3-të"
        latitude = "".join(
            d.xpath(f'.//preceding::li[text()="{location_name}"]/@data-map-latitude')
        )
        longitude = "".join(
            d.xpath(f'.//preceding::li[text()="{location_name}"]/@data-map-longitude')
        )
        phone = (
            "".join(
                d.xpath('.//*[contains(text(), " Phone ")]/following-sibling::text()')
            )
            .replace(":", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/*[contains(text(), " Working Hours ")]/following-sibling::text()'
                )
            )
            .replace(": ", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
