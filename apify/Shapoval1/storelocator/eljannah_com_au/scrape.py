from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://eljannah.com.au"
    page_url = "https://eljannah.com.au/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-item"]')
    for d in div:

        location_name = "".join(d.xpath(".//h5/text()"))
        ad = (
            "".join(d.xpath(".//h5/following-sibling::div[1]//text()"))
            .replace("\n", "")
            .replace(", Australia", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "AU"
        city = location_name
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "let locations")]/text()'))
            .split(f"{location_name.split('–')[0].strip()}")[1]
            .split(",")[1]
            .replace("'", "")
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "let locations")]/text()'))
            .split(f"{location_name.split('–')[0].strip()}")[1]
            .split(",")[2]
            .replace("'", "")
            .replace("]", "")
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath('.//span[@class="opening-hours"]/following-sibling::text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if location_name.find("Coming Soon") != -1:
            city = city.split("–")[0].strip()
            hours_of_operation = "Coming Soon"

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
