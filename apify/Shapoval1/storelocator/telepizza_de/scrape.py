from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.telepizza.de/"
    api_url = "https://www.telepizza.de/bestellen"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//tr[@data-id]")
    for d in div:

        slug = "".join(d.xpath('.//a[@class="storelink"]/@href'))
        page_url = f"https://www.telepizza.de{slug}"
        location_name = (
            "".join(d.xpath('.//a[@class="storelink"]/text()'))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(d.xpath('.//span[@itemprop="streetAddress"]/text()'))
        state = "".join(d.xpath(".//@data-state"))
        postal = "".join(d.xpath('.//span[@itemprop="postalCode"]/text()'))
        country_code = "DE"
        city = "".join(d.xpath(".//@data-city"))
        store_number = "".join(d.xpath(".//@data-id"))
        phone = "".join(d.xpath('.//span[@itemprop="telephone"]/text()'))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[./strong[text()="Öffnungszeiten:"]]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("06.06.") != -1:
            hours_of_operation = hours_of_operation.split("06.06.")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
