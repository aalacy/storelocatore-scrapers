from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://samsxpresscarwash.com"
    api_url = "https://samsxpresscarwash.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="columns store-location-block"]')
    for d in div:

        page_url = "".join(d.xpath(".//a[./h6]/@href"))
        location_name = "".join(d.xpath(".//a/h6/text()")).replace("\n", "").strip()
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-long"))
        cms = "".join(d.xpath('.//span[contains(text(), "Coming Soon")]/text()'))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(tree.xpath('//p[./a[text()="Directions"]]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = (
            "".join(tree.xpath('//div[@class="wysiwg-content"]//h6/text()')).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Hours of Operation"]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if cms:
            location_name = location_name + " - " + "Coming Soon"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
