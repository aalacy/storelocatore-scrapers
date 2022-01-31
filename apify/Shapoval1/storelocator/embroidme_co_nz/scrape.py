from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://embroidme.co.nz/"
    api_url = "https://embroidme.co.nz/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="row store-link-row"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="store-heading-link"]/@href'))
        ad = (
            "".join(
                d.xpath(
                    './/div[@class="col-sm-7"]//p[@class="store-address-link"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        location_name = (
            "EmbroidMe"
            + " "
            + "".join(d.xpath('.//a[@class="store-heading-link"]/text()'))
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NZ"
        city = a.city or "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="col-sm-2"]//p[@class="store-address-link"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        latitude = map_link.split("query=")[1].split(",")[0].strip()
        longitude = map_link.split("query=")[1].split(",")[1].strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="store-hours-container"]/*//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        cls = "".join(
            tree.xpath('//p[contains(text(), "We will be closed for")]/text()')
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
