from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.babeland.com/"
    api_url = "https://www.babeland.com/content/c/Babeland_Store_Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="shopInfo section group"]')

    for d in div:
        relocat = "".join(d.xpath('.//img[@alt="Mercer relocation"]/@alt'))
        if relocat:
            continue
        page_url = "https://www.babeland.com/content/c/Babeland_Store_Locations"
        location_name = "".join(d.xpath(".//h3/a/text()"))
        street_address = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[1]/li[1]/text()'
            )
        )
        ad = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[1]/li[2]/text()'
            )
        )

        phone = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[4]/li/text()'
            )
        ).strip()
        state = " ".join(ad.split(",")[1].split()[:-1]).strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[3]//text()'
                )
            )
            .replace("\r\n", " ")
            .replace("   ", " ")
            .replace("    ", " ")
            .strip()
        )

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
