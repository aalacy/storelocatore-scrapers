from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[@class="store-item card"]')

    for d in div:
        location_name = "".join(d.xpath('.//p[@class="h3 card-title"]/text()'))
        ad = d.xpath(".//address/text()")
        raw_address = " ".join(ad)

        city = ad.pop()
        street_address = " ".join(ad[:-1])
        phone = "".join(d.xpath('.//ul[@class="card-block"]/li[1]/text()'))
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr//text()")).replace("\n", "").strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="SN",
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://decathlon.sn"
    page_url = "https://decathlon.sn/magasins"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
