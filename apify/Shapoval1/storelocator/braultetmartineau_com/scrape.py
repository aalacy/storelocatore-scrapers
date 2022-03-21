from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.braultetmartineau.com"
    page_url = "https://www.braultetmartineau.com/en/store-finder?InitMap=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store-list-address col-md-3 col-xs-12 col-sm-6"]')

    for d in div:

        location_name = (
            "".join(d.xpath(".//div[@class='store-name-label']/text()"))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(d.xpath('.//span[@class="addressline1"]/text()'))
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("Tel.", "")
            .replace("\n", "")
            .strip()
        )
        state = "".join(d.xpath('.//span[@class="province"]/text()'))
        postal = "".join(d.xpath('.//span[@class="postalcode"]/text()'))
        country_code = "CA"
        city = "".join(d.xpath('.//span[@class="city"]/text()'))
        hours_of_operation = (
            " ".join(d.xpath('.//table[@class="store-opening-hours"]//tr//td//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
