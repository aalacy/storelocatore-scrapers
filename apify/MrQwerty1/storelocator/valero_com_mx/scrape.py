from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode or ""

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://valero.com.mx/stations-valero/?lang=en"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[./div[@class='list-item']]")
    for d in divs:
        location_name = "".join(d.xpath(".//h6[@class='title']/text()")).strip()
        raw_address = (
            "".join(d.xpath(".//div[@class='desc']//text()"))
            .strip()
            .replace("\n", ", ")
        )
        phone = "".join(d.xpath("./following-sibling::div[1]//text()")).strip()
        if "Obtener" in phone:
            phone = SgRecord.MISSING
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        if "–" in phone:
            phone = phone.split("–")[0].strip()
        street_address, city, state, postal = get_international(raw_address)
        postal = postal.replace("C.P.", "").strip()
        text = "".join(d.xpath("./following-sibling::div[3]//a/@href"))
        if ("!3d" and "!4d") in text:
            latitude = text.split("!3d")[1].split("!")[0]
            longitude = text.split("!4d")[1].split("!")[0].split("?")[0]
        elif "@" in text:
            latitude, longitude = text.split("@")[1].split("/")[0].split(",")[:2]
        elif ("//" and ",") in text:
            latitude, longitude = text.split("//")[-1].split(",")
        else:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MX",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://valero.com.mx/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
