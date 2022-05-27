from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[./span[contains(text(), "Opening hours")]]')
    for d in div:

        location_name = "".join(d.xpath(".//preceding::h2[1]//text()"))
        street_address = "".join(
            d.xpath(
                './/preceding::a[contains(@href, "https://ul.waze.com/")][1]//text()'
            )
        )
        country_code = "IL"
        city = "".join(d.xpath(".//preceding::h2[1]//text()"))
        text = "".join(
            d.xpath('.//preceding::a[contains(@href, "https://ul.waze.com/")][1]/@href')
        )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split("%2C")[0]
                longitude = text.split("ll=")[1].split("%2C")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        phone = "".join(d.xpath('.//preceding::a[contains(@href, "phone")][1]/text()'))
        hours_of_operation = (
            " ".join(d.xpath(".//following::div[1]//text()")).replace("\n", "").strip()
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.decathlon.co.il/en/"
    page_url = "https://www.decathlon.co.il/en/content/42-our-stores"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
