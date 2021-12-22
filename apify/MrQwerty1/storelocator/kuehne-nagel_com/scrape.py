import re
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
    postal = adr.postcode or SgRecord.MISSING
    country = adr.country or ""

    return street_address, city, state, postal, country


def clean_phone(text):
    text = str(text).replace("?", "")
    black_list = [",", ";", "/", "or", "|", "ext", "x"]
    for b in black_list:
        if b in text.lower():
            text = text.lower().split(b)[0].strip()

    text = text.replace("(imp", "")
    return text


def fetch_data(sgw: SgWriter):
    page_url = "https://home.kuehne-nagel.com/locations"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='bg-white component']")
    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = " ".join(
            " ".join(
                d.xpath(".//p[@class='location__address text-14 mb-0']/text()")
            ).split()
        )
        if "canada" in raw_address.lower():
            country = "Canada"
            state = SgRecord.MISSING
            postal = re.findall(r"[A-Z]\d[A-Z]\s\d[A-Z]\d", raw_address).pop(0)
            city = raw_address.split(postal)[-1].replace("CANADA", "").strip()
            street_address = raw_address.split(postal)[0].strip()
        else:
            street_address, city, state, postal, country = get_international(
                raw_address
            )

        if street_address.isnumeric() or len(street_address) < 7:
            separator = street_address
            street_address = raw_address.split(separator)[0] + f" {separator}"

        phones = d.xpath(".//p[@class='location__phone text-14 mb-0']/text()")
        for p in phones:
            if "phone" in p.lower() and "contact" not in p.lower():
                phone = p.lower().replace("phone", "").replace("contact", "").strip()
                phone = clean_phone(phone)
                break
        else:
            phone = SgRecord.MISSING

        hours = d.xpath(".//p[@class='location__hours text-14 mb-0']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours).replace("\n", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://home.kuehne-nagel.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
