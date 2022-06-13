from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "freddy-fresh_de"
    api_url = "https://webshop.freddy-fresh.de/storedata/listStore"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="row-fluid store-item"]')
    for d in div:

        slug = "".join(d.xpath('.//a[text()="Liefergebiete"]/@href'))
        page_url = f"https://webshop.freddy-fresh.de{slug}"
        location_name = "".join(d.xpath('.//h2[@class="store-name"]/text()'))
        ad = "".join(d.xpath('.//p[@class="store-address"]/text()'))
        street_address = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[0].strip()
        country_code = "DE"
        city = " ".join(ad.split(",")[1].split()[1:]).strip()
        store_number = "".join(d.xpath("./@data-store-id"))
        phone = (
            "".join(d.xpath('.//p[@class="store-tel"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                d.xpath('.//span[@class="store-opening-list row-fluid"]/span//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
