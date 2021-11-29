from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.bankunited.com/contact-us/find-a-branch-atm?loc=10001&radius=3000",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.bankunited.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = '{"Latitude":40.75368539999999,"Longitude":-73.9991637,"Radius":"3000","ShowDisasterView":"False"}'

    r = session.post(
        "https://www.bankunited.com/contact-us/find-a-branch-atm/GetLocations",
        headers=headers,
        data=data,
    )
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "row marker-row ")]')
    for d in div:

        page_url = "https://www.bankunited.com/contact-us/find-a-branch-atm"
        location_name = "".join(d.xpath('.//h2[@itemprop="name"]/text()'))
        location_type = (
            "".join(d.xpath('.//div[@data-lat]/p[@class="p-12"][1]//text()'))
            .replace("\r\n", "")
            .strip()
        )
        location_type = " ".join(location_type.split())

        street_address = (
            "".join(d.xpath('.//span[@itemprop="streetAddress"]/text()')).strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = "".join(
                d.xpath(
                    './/span[@itemprop="streetAddress"]/following-sibling::span[1]//text()'
                )
            ).strip()
        state = "".join(d.xpath('.//span[@itemprop="addressRegion"]/text()')).strip()
        postal = "".join(d.xpath('.//span[@itemprop="postalCode"]/text()')).strip()
        country_code = "USA"
        city = "".join(d.xpath('.//span[@itemprop="addressLocality"]/text()')).strip()
        latitude = "".join(d.xpath(".//div/@data-lat"))
        longitude = "".join(d.xpath(".//div/@data-lng"))
        phone = (
            "".join(d.xpath('.//span[@itemprop="telephone"]/text()')).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            "".join(d.xpath('.//span[@itemprop="openingHours"]/text()')).strip()
            or "<MISSING>"
        )
        tmpcls = "".join(
            d.xpath('.//*[contains(text(), "Temporarily Closed")]//text()')
        )
        if tmpcls:
            hours_of_operation = "Temporarily Closed"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.bankunited.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
