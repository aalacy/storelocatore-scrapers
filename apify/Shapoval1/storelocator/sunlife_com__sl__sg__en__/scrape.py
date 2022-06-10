from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sunlife.com/sl/"
    api_url = "https://www.sunlife.com/sl/sg/en/contact-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = "https://www.sunlife.com/sl/sg/en/contact-us/"
    location_name = (
        "".join(tree.xpath('//h2[text()="Address"]/following-sibling::p[1]//text()'))
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(tree.xpath('//h2[text()="Address"]/following-sibling::p[2]//text()'))
        .replace("\n", "")
        .strip()
    )
    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "Singapore"
    city = a.city or "<MISSING>"
    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=SgRecord.MISSING,
        raw_address=ad,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
