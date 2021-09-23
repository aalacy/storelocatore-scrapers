from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tacobell.com.ph"
    api_url = "https://tacobell.com.ph/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="find-Us-Branches"]')
    for d in div:

        page_url = "https://tacobell.com.ph/locations/"
        location_name = "".join(d.xpath(".//h5/text()"))
        ad = (
            " ".join(d.xpath('.//p[@class="findus_addr"]/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Phillippines"
        city = a.city or "<MISSING>"
        if location_name == "TACO BELL SM MEGAMALL":
            city = "Mandaluyong City"
        latitude = (
            "".join(
                d.xpath(
                    './/a[./button[@class="primary find-Us-Branches-Dir-btn"]]/@href'
                )
            )
            .split("q=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    './/a[./button[@class="primary find-Us-Branches-Dir-btn"]]/@href'
                )
            )
            .split("q=")[1]
            .split(",")[1]
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = "".join(
            d.xpath('.//p[@class="opening_hours"]/text()')
        ).strip()
        if hours_of_operation.find("Seasonal") != -1:
            hours_of_operation = "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
