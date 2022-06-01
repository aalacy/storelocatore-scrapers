import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    postal = re.findall(r"\d{4}", line).pop()
    adr = parse_address(International_Parser(), line, postcode=postal)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[@class='day']")
    for h in hours:
        day = "".join(h.xpath("./span/text()")).strip()
        inter = "".join(h.xpath("./text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.ufcgym.com.au/find-a-gym/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-lg-4 col-md-6 gym-column with-info']")

    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='gym-name']/a/text()")).strip()
        raw_address = " ".join(d.xpath(".//div[@class='address']/text()")).strip()
        if ")" in raw_address:
            raw_address = raw_address.split(")")[-1].strip()
        street_address, city, state, postal = get_international(raw_address)
        if city == SgRecord.MISSING:
            if "Sydney" in raw_address:
                city = "Sydney"
            else:
                city = location_name
        country_code = "AU"
        slug = "".join(d.xpath(".//a[contains(text(), 'Visit')]/@href"))
        page_url = f"https://www.ufcgym.com.au{slug}"
        phone = "".join(d.xpath(".//a[@class='telno-link']/text()")).strip()
        latitude, longitude = "".join(d.xpath(".//div/@data-location")).split(",")
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.ufcgym.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
