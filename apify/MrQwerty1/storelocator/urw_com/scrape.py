from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    state = state.replace("/", "").strip()
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    locations = []
    pp = tree.xpath("//div[@class='rich-text']/p")
    pp.pop(0)
    _tmp = []
    for p in pp:
        text = " ".join("".join(p.xpath(".//text()")).split())
        if "HEADQUARTERS" in text or "EUROPE" in text or "UNITED STATES" in text:
            continue
        if p.xpath("./strong"):
            locations.append(_tmp)
            _tmp = [text]
            continue
        _tmp.append(text)

    locations.pop(0)
    locations.append(_tmp)

    for loc in locations:
        location_name = loc.pop(0)
        phone = loc.pop().replace("T.", "").strip()
        raw_address = ", ".join(loc)
        if "Paris" not in raw_address:
            street_address, city, state, postal = get_international(raw_address)
        else:
            state = SgRecord.MISSING
            street_address = loc.pop(0)
            postal = loc.pop().split()[0]
            city = "Paris"

        if city == SgRecord.MISSING and "Praha" in raw_address:
            city = "Praha"
        if "New York" in location_name or "Angeles" in location_name:
            country_code = "US"
        else:
            country_code = location_name.replace("The", "").strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.urw.com/"
    page_url = "https://www.urw.com/Locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
