from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.beefjerkyoutlet.com"
    api_url = "https://www.beefjerkyoutlet.com/location-finder"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-content"]')

    for d in div:
        slug = "".join(d.xpath('.//a[@class="btn-yellow"]/@href'))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//h4/text()"))
        street_address = (
            "".join(d.xpath('.//span[@class="address-line1"]/text()'))
            + " "
            + "".join(d.xpath('.//span[@class="address-line2"]/text()'))
        )
        street_address = (
            street_address.replace("in Quil Ceda Village", "")
            .replace("Concord Mills Mall", "")
            .strip()
        )
        if street_address.find("Grove City Premium Outlets") != -1:
            street_address = street_address.split("Grove City Premium Outlets")[
                0
            ].strip()
        if street_address.find("Tanger Outlet Center") != -1:
            street_address = street_address.split("Tanger Outlet Center ")[0].strip()
        if street_address.find("Suite #816 Suite #816") != -1:
            street_address = street_address.replace(
                "Suite #816 Suite #816", "Suite #816"
            ).strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        state = (
            "".join(d.xpath('.//span[@class="administrative-area"]/text()'))
            or "<MISSING>"
        )
        postal = "".join(d.xpath('.//span[@class="postal-code"]/text()')) or "<MISSING>"
        country_code = "US"
        city = "".join(d.xpath('.//span[@class="locality"]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[@class="paragraph paragraph--type--store-hours paragraph--view-mode--default"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if (
            hours_of_operation == "<MISSING>"
            and page_url != "https://www.beefjerkyoutlet.com/node/28"
        ):
            r = session.get(page_url, headers=headers)

            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//span[contains(text(), "Store Hours")]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("Hours may vary Please call for hours", "")
            .replace(
                "Closed New Years Day, Easter Sunday, Thanksgiving Day, Christmas.", ""
            )
            .replace(
                "For Curbside Orders please call during normal business hours to schedule your Pickup",
                "",
            )
            .strip()
        )
        if hours_of_operation.find("Now Open") != -1:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.replace("OPEN DAILY!", "").strip()
        if hours_of_operation.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"
        if phone == "<MISSING>":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="description-hours-wrapper"]//span[text()="Phone"]/following-sibling::div/text()'
                    )
                )
                or "<MISSING>"
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
