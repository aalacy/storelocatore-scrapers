import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    post = line.split(", ")[-1]
    adr = parse_address(International_Parser(), line, postcode=post)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return ";".join(
        tree.xpath("//h4[contains(text(), 'Hours')]/following-sibling::*[1]/text()")
    )


def fetch_data(sgw: SgWriter):
    api = "https://www.rightathome.co.uk/find-your-local-office/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div/@data-results"))
    js = json.loads(text)

    for j in js:
        location_name = j.get("name") or ""
        source = j.get("address")
        if "{" in source or not source:
            continue

        root = html.fromstring(source)
        line = root.xpath("//text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        street_address, city, postal = get_international(raw_address)
        if city == SgRecord.MISSING:
            city = location_name.replace("Right at Home", "").split(":")[0].strip()
        country_code = "GB"
        store_number = j.get("id")
        slug = j.get("url")
        page_url = f"https://www.rightathome.co.uk{slug}"
        phone = j.get("phoneNumber") or ""
        if "," in phone:
            phone = phone.split(",")[0].strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = get_hoo(page_url)

        if ", 24/7" in hours_of_operation:
            hours_of_operation = hours_of_operation.split(", 24/7")[0].strip()
        if ", Out" in hours_of_operation:
            hours_of_operation = hours_of_operation.split(", Out")[0].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rightathome.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
