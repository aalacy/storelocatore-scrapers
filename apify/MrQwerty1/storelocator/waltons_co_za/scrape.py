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

    return street, city


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='row location-container']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@class='location-name']/text()")).strip()
        raw_address = "".join(d.xpath(".//p[@class='location-address']/text()")).strip()
        postal = raw_address.split(",")[-1].strip()
        if raw_address.endswith(","):
            raw_address = raw_address[:-1]

        state = "".join(d.xpath("./@data-region"))
        street_address, city = get_international(raw_address)
        country_code = "ZA"
        phone = (
            "".join(d.xpath(".//p[@class='location-phone']/text()"))
            .replace("Phone:", "")
            .strip()
        )
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        latitude = "".join(d.xpath("./@data-latitude"))
        longitude = "".join(d.xpath("./@data-longitude"))
        hours_of_operation = ";".join(d.xpath(".//p[not(@class)]/text()"))

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
    locator_domain = "https://www.waltons.co.za/"
    page_url = "https://www.waltons.co.za/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
