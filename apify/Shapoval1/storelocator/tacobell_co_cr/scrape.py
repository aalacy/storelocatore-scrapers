from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobell.co.cr/"
    api_url = "https://www.tacobell.co.cr/restaurantes"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "tab filter-data div-link")]')
    for d in div:
        slug = "".join(d.xpath("./@id"))
        page_url = f"https://www.tacobell.co.cr/restaurantes/{slug}"

        location_name = "".join(d.xpath("./@data-nombre"))
        state = "".join(d.xpath("./@data-provincia"))
        country_code = "Costa Rica"
        latitude = (
            "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
            .split("q=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
            .split("q=")[1]
            .split(",")[1]
            .split("h")[0]
            .strip()
        )
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Contacto:")]/text()'))
            .replace("Contacto:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//p[./span[@class="big"]]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=SgRecord.MISSING,
            city=SgRecord.MISSING,
            state=state,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
