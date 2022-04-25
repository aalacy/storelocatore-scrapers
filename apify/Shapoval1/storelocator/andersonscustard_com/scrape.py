from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://andersonscustard.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="trailer_box "]//a')
    for d in div:

        page_url = "https://andersonscustard.com" + "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="title"]/text()'))
        street_address = "".join(
            tree.xpath('//h4[text()="Store Address"]/following-sibling::p/text()[1]')
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h4[text()="Store Address"]/following-sibling::p/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(tree.xpath('//script[@id="google-maps-js-after"]/text()'))
            .split("LatLng(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[@id="google-maps-js-after"]/text()'))
            .split("LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//h4[text()="Store Address"]/following-sibling::p/text()[3]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Store Hours"]/following-sibling::ul/li//text()'
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://andersonscustard.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
