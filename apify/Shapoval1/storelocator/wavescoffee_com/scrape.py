from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wavescoffee.com"
    api_url = "https://wavescoffee.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="all-locations-tab"]/ul/li')
    for d in div:

        location_name = (
            "".join(
                d.xpath(
                    './/div[contains(@class, "post-details padding-3")]/*[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if not location_name:
            continue
        slug = "".join(
            d.xpath('.//div[contains(@class, "post-details padding-3")]/*[1]//@href')
        )
        page_url = "https://wavescoffee.com/locations"
        if slug:
            page_url = f"https://wavescoffee.com/{slug}"
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "CA"
        city = "<MISSING>"
        if page_url == "https://wavescoffee.com/locations":
            street_address = "".join(
                d.xpath(
                    './/div[contains(@class, "post-details padding-3")]/*[1]/following-sibling::p[1]/text()[1]'
                )
            )
            city = (
                "".join(
                    d.xpath(
                        './/div[contains(@class, "post-details padding-3")]/*[1]/following-sibling::p[1]/text()[2]'
                    )
                )
                .split(",")[0]
                .strip()
            )
            state = (
                "".join(
                    d.xpath(
                        './/div[contains(@class, "post-details padding-3")]/*[1]/following-sibling::p[1]/text()[2]'
                    )
                )
                .split(",")[1]
                .strip()
            )
        cms = "".join(d.xpath('.//*[contains(text(), "Opening Early")]/text()'))
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if cms:
            hours_of_operation = "Coming Soon"
        if slug:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            ad = (
                " ".join(
                    tree.xpath('//*[text()="Address"]/following-sibling::*[1]/text()')
                )
                .replace("\n", " ")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
            phone = (
                "".join(
                    tree.xpath('//*[text()="Phone"]/following-sibling::*[1]/text()')
                )
                .replace("\n", "")
                .replace("T:", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//*[contains(text(), "Hours")]/following-sibling::div[1]/div//text()'
                    )
                )
                .replace("\n", "")
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
