from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitnessme.com"
    api_url = "https://johnsonfitnessme.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://johnsonfitnessme.com/contact/"
    ad = (
        " ".join(
            tree.xpath(
                '//div[./div/h2[text()="Info"]]/following-sibling::div[1]//p/a/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    a = parse_address(International_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    state = a.state or "<MISSING>"
    postal = (
        "".join(
            tree.xpath(
                '//div[./div/h2[text()="Info"]]/following-sibling::div[1]//p/a[last()]/text()'
            )
        )
        .replace("\n", "")
        .split()[-1]
        .strip()
    )
    country_code = a.country or "<MISSING>"
    city = a.city or "<MISSING>"
    text = " ".join(
        tree.xpath(
            '//div[./div/h2[text()="Info"]]/following-sibling::div[1]//p/a/@href'
        )
    )
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    phone = (
        " ".join(
            tree.xpath(
                '//div[./div/h2[text()="Info"]]/following-sibling::div//a[contains(@href, "tel")]/@href'
            )
        )
        .replace("tel:", "")
        .replace("\n", "")
        .strip()
    )
    info = tree.xpath("//footer//p/text()")
    location_name = "".join(info[0]).strip()

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
