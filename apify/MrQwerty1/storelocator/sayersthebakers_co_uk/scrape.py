from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def fetch_data(sgw: SgWriter):
    page_url = "https://sayersthebakers.co.uk/Store-List/50/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//p[./strong]")

    for d in divs:
        location_name = "".join(d.xpath("./strong/text()")).strip()
        lines = d.xpath("./text()")
        lines = list(filter(None, [li.strip() for li in lines]))
        hours_of_operation = lines.pop()
        line = lines.pop()
        phone = line.split("|")[0].replace("Tel:", "").strip()
        raw_address = line.split("|")[-1].strip()
        postal = raw_address.split(",")[-1].strip()
        arg = ",".join(raw_address.split(",")[:-1])
        street_address, city = get_international(arg)
        if city == SgRecord.MISSING:
            city = arg.split(",")[-1].strip()
            street_address = street_address.replace(city, "").strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://sayersthebakers.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
