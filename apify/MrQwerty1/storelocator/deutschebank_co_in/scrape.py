import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING

    return city, state


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='location' and contains(@id, 'branch')]//tr[.//a[contains(@href, 'javascript:')]]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//strong/text()")).strip()
        raw_address = "".join(d.xpath("./following-sibling::tr[1]//text()")).strip()
        city, state = get_international(raw_address)
        postal = "".join(re.findall(r"\d{6}|\d{3} \d{3}", raw_address))
        street_address = raw_address.split(city)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        country_code = "IN"
        try:
            phone = d.xpath(
                "./following-sibling::tr[.//b[contains(text(), 'Phone')]]/td[2]/text()"
            )[0].strip()
        except IndexError:
            phone = SgRecord.MISSING

        text = "".join(d.xpath(".//a/@onclick"))
        latitude, longitude = text.split("showAddress(")[1].split(",")[:2]
        try:
            hours_of_operation = (
                d.xpath(
                    "./following-sibling::tr[.//b[contains(text(), 'Hours')]]/td[2]/text()"
                )[0]
                .replace("*", "")
                .strip()
            )
        except IndexError:
            hours_of_operation = SgRecord.MISSING

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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://deutschebank.co.in/"
    page_url = "https://forms.deutschebank.co.in/atm_branch_locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
