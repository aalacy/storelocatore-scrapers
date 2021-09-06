from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.lv/en/"
    api_url = "https://www.ikea.lv/en/page/contactsriga"
    session = SgRequests()
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
        .split(",")[0]
        .strip()
    )
    state = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Address")]/following-sibling::text()[3]'
            )
        )
        .split(",")[1]
        .strip()
    )
    postal = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Address")]/following-sibling::text()[3]'
            )
        )
        .split(",")[2]
        .strip()
    )
    country_code = "LV"
    city = (
        "".join(
            tree.xpath(
                '//strong[contains(text(), "Address")]/following-sibling::text()[1]'
            )
        )
        .split(",")[1]
        .strip()
    )
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
        " ".join(
            tree.xpath(
                '//strong[contains(text(), "Store opening hours")]/following-sibling::text()[1]'
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

    locator_domain = "https://www.ikea.lt/en/"
    api_url = "https://www.ikea.lt/en/contactsvilnius"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://www.ikea.lv/en/page/contactsriga"
    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
    street_address = (
        "".join(
            tree.xpath('//b[contains(text(), "Address")]/following-sibling::text()[1]')
        )
        .replace(",", "")
        .strip()
    )
    postal = (
        "".join(
            tree.xpath('//b[contains(text(), "Address")]/following-sibling::text()[2]')
        )
        .replace("\n", "")
        .split()[0]
        .strip()
    )
    country_code = "LT"
    city = (
        "".join(
            tree.xpath('//b[contains(text(), "Address")]/following-sibling::text()[2]')
        )
        .replace("\n", "")
        .split()[1]
        .strip()
    )
    phone = (
        "".join(
            tree.xpath(
                '//b[contains(text(), "Phone numbers:")]/following-sibling::text()[1]'
            )
        )
        .replace("\n", "")
        .replace("Customer service:", "")
        .strip()
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//b[contains(text(), "Store opening hours")]/following-sibling::text()[1]'
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
        state=SgRecord.MISSING,
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
