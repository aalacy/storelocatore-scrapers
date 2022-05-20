from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumphmotorcycles.co.kr/"
    api_url = "https://www.triumphmotorcycles.co.kr/dealers/korea"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "map-location__content")]')
    for d in div:

        page_url = "https://www.triumphmotorcycles.co.kr/dealers/korea"
        location_name = "".join(d.xpath('.//h2[@class="title--style-b"]/text()'))
        ad = (
            " ".join(
                d.xpath(
                    './/h2[@class="title--style-b"]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "KR"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//preceding-sibling::div[1]//div/@data-map-lat"))
        longitude = "".join(d.xpath(".//preceding-sibling::div[1]//div/@data-map-lon"))
        phone = (
            "".join(
                d.xpath(
                    './/p[./span[text()="Contact Details:"]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .replace("☎", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//p[./span[contains(text(), "Opening Hours")]]//text()'))
            .replace("\n", "")
            .replace("Opening Hours:", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
