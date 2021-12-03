from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.am"
    api_url = "https://jysk.am/addresses/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = "https://jysk.am/addresses/"
    ad = (
        " ".join(tree.xpath('//a[contains(@href, "mail")]/preceding-sibling::text()'))
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )

    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "AM"
    city = a.city or "<MISSING>"
    map_link = "".join(tree.xpath('//a[text()="View Larger Map"]/@href'))
    latitude = map_link.split("mlat=")[1].split("&")[0].strip()
    longitude = map_link.split("mlon=")[1].split("#")[0].strip()
    phone = (
        " ".join(
            tree.xpath('//a[contains(@href, "mail")]/following-sibling::text()[2]')
        )
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=SgRecord.MISSING,
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
