from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.lv/en"
    api_url = "https://www.ikea.lv/en/page/contactsriga"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = "https://www.ikea.lv/en/page/contactsriga"
    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()

    street_address = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Address")]/following-sibling::text()[1]'
            )
        )
        .replace("\n", "")
        .replace(",", "")
        .strip()
    )
    ad = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Address")]/following-sibling::text()[2]'
            )
        )
        .replace("\n", "")
        .strip()
    )
    state = "<MISSING>"
    postal = ad.split(",")[2].strip()
    country_code = "LV"
    city = ad.split(",")[1].strip()
    phone = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Contact us")]/following-sibling::text()[1]'
            )
        )
        .replace("\n", "")
        .replace("Customer service:", "")
        .strip()
    )
    hours_of_operation = (
        "".join(
            tree.xpath(
                '//strong[text()="Store opening hours"]/following-sibling::text()[1]'
            )
        )
        .replace("\n", "")
        .strip()
    )
    cls = "".join(tree.xpath('//span[contains(text(),"are closed")]/text()'))
    if cls:
        hours_of_operation = "Closed"

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

    locator_domain = "https://www.ikea.lt/en"
    api_url = "https://www.ikea.lt/en/contactsvilnius"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[@class="nav-item pb-2 px-3"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.ikea.lt{slug}"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
        street_address = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "Address:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "Address:")]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )

        state = "<MISSING>"
        postal = ad.split()[0].strip()
        country_code = "LT"
        city = ad.split()[1].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "Phone numbers:")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .replace("Customer service:", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "pening")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
