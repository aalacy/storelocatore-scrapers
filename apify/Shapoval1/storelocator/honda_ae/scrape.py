from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.ae/"
    api_url = "https://www.honda.ae/cars/locations/?city=&businessFunctions=Sales"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "list-item locations listing")]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@title="Full Details"]/@href'))
        page_url = "https:" + page_url
        location_name = "".join(d.xpath(".//h3//text()"))
        location_type = "Showroom"
        street_address = (
            "".join(d.xpath('.//span[@class="address-line1"]/text()'))
            .replace(",", "")
            .strip()
        )
        country_code = "AE"
        city = (
            "".join(d.xpath('.//span[@class="address-city"]/text()'))
            .replace(",", "")
            .strip()
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ll = "".join(tree.xpath('//iframe[@class="map"]/@src'))
        latitude = ll.split("q=")[1].split(",")[0].strip()
        longitude = ll.split("q=")[1].split(",")[1].split("&")[0].strip()
        phone = (
            "".join(tree.xpath('//span[contains(@class, "telephony")]/text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="loc-hours-table"]//tr/td//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
