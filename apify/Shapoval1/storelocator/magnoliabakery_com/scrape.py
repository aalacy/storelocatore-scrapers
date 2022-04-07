from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.magnoliabakery.com/"
    api_url = "https://www.magnoliabakery.com/pages/store-location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="NavList__wrapper NavList__wrapper--multiple-subheadings"]//a[contains(@href, "/blogs/stores/")]'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.magnoliabakery.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//meta[contains(@property, "title")]/@content')
        )
        ad = (
            " ".join(
                tree.xpath(
                    '//main[@id="MainContent"]//section[@id="sectionContentArea--Store"]/div[@class="ContentArea__placeholder"]//i[@class="StoreInformation__detail-icon far fa-map-marker-alt"]/following-sibling::a[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = (
            " ".join(
                tree.xpath(
                    '//main[@id="MainContent"]//section[@id="sectionContentArea--Store"]/div[@class="ContentArea__placeholder"]//i[@class="StoreInformation__detail-icon far fa-phone-alt"]/following-sibling::a[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//main[@id="MainContent"]//section[@id="sectionContentArea--Store"]/div[@class="ContentArea__placeholder"]//div[@class="StoreInformation__detail StoreInformation__detail--hours-of-operation"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Hours of Operation", "")
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
