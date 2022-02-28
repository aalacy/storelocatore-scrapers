from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fullypromoted.com.au/"
    api_url = "https://fullypromoted.com.au/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="row store-link-row"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="store-heading-link"]/@href'))
        location_name = (
            "".join(d.xpath('.//a[@class="store-heading-link"]/text()'))
            .replace("\n", "")
            .strip()
        )
        location_name = " ".join(location_name.split())
        ad = (
            "".join(d.xpath('.//p[@class="store-address-link"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        adr = (
            "".join(tree.xpath('//div[@class="contact-box-address"]/p/text()[last()]'))
            .replace("\n", "")
            .strip()
        )
        state = adr.split()[-2].strip()
        postal = adr.split()[-1].strip()
        country_code = "AU"
        city = " ".join(adr.split()[:-2]).strip()
        latitude = (
            "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
            .split("q=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
            .split("q=")[1]
            .split(",")[1]
            .strip()
        )
        if longitude.find("h") != -1:
            longitude = longitude.split("h")[0].strip()
        phone = (
            "".join(
                tree.xpath('//div[@class="contact-phone-container"]/a/text()')
            ).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="store-hours-container"]/*//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        cls = "".join(
            tree.xpath(
                '//p[contains(text(), "We will be closed from")]/text() | //p[contains(text(), "1st day back")]/text() | //p[contains(text(), "REOPEN")]/text()'
            )
        )
        if cls:
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
