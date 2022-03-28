from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dennys.co.nz"
    api_url = "https://dennys.co.nz/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p/a[contains(@href, "tel")]]')
    for d in div:

        page_url = "https://dennys.co.nz/locations/"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = (
            " ".join(d.xpath('.//b[text()="Address"]/following-sibling::text()[1]'))
            .replace("\n", "")
            .strip()
        )

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NZ"
        city = a.city or "<MISSING>"
        map_link = "".join(d.xpath(".//preceding::iframe[1]/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            " ".join(d.xpath('.//b[text()="Phone"]/following-sibling::a[1]/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//p//text()"))
            .replace("\n", "")
            .split("Opening Hours")[1]
            .split("Address")[0]
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
