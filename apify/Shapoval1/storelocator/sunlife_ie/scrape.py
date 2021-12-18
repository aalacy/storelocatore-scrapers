from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sunlife.ie/"
    api_url = "https://www.sunlife.ie/en/contact-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://www.sunlife.ie/en/contact-us/"
    location_name = (
        "".join(tree.xpath("//div[./h1]/p[last()]/text()[1]")).replace("\n", "").strip()
    )
    ad = (
        " ".join(tree.xpath("//div[./h1]/p[last()]/text()[position()>1]"))
        .replace("\n", "")
        .split("Ph")[0]
        .strip()
    )
    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "IE"
    city = a.city or "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[./h1]/p[last()]/text()[position()>1]"))
        .replace("\n", "")
        .split("Ph:")[1]
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
