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
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def get_raw_address(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    raw_address = " ".join(
        tree.xpath(
            "//h3[contains(text(), 'Address')]/following-sibling::div[1]//p/text()"
        )
    ).strip()

    return raw_address


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    phone = "".join(
        tree.xpath("//span[@class='info']/a[contains(@href, 'tel:')]/text()")
    ).strip()

    _tmp = []
    hours = tree.xpath(
        "//h3[contains(text(), 'Hours') or contains(text(), 'HOURS')]/following-sibling::div[1]//p|//h3[contains(text(), 'Hours') or contains(text(), 'HOURS')]/following-sibling::div[1]//span"
    )
    black_list = ["HOLIDAYS", "Regular", "CHRISTMAS", "XMAS"]
    for h in hours:
        line = " ".join("".join(h.xpath(".//text()")).split()).strip()
        if not line:
            continue
        if "staff" in line.lower():
            break
        if line.endswith(":") or (":" not in line and "24" not in line):
            continue

        for b in black_list:
            if b in line:
                break
        else:
            _tmp.append(line)
            if "24" in line:
                break

    hours_of_operation = ";".join(_tmp)

    return phone, hours_of_operation


def fetch_data(sgw: SgWriter):
    api = "https://www.energiefitness.com/bin/public/energie-fitness/consumer/gyms/getGymInfo"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        source = j.get("markerDescription") or "<html>"
        tree = html.fromstring(source)
        slug = "".join(tree.xpath(".//a/@href"))
        page_url = f"https://www.energiefitness.com{slug}"

        line = tree.xpath(".//p//text()")
        line = list(filter(None, [li.strip() for li in line]))

        if line:
            raw_address = " ".join(line)
            _t = line[-1]
            postal = " ".join(
                re.findall(r"([A-Z\d]{2,4} [A-Z\d]+|\d{5}|[A-Z\d]{3})", _t)
            )
        else:
            postal = SgRecord.MISSING
            raw_address = get_raw_address(page_url)

        adr = raw_address.replace(postal, "").strip()
        street_address, city = get_international(adr)
        if city == SgRecord.MISSING and "Dublin" in raw_address:
            city = "Dublin"
        if city == SgRecord.MISSING:
            city = location_name
            if " St " in city:
                city = city.split(" St ")[0].strip()
        if len(street_address) < 3:
            street_address = raw_address.split(city)[0].strip()

        if postal.isdigit():
            country_code = "ES"
        elif "Bahrain" in raw_address:
            country_code = "BH"
        elif "Dublin" in raw_address:
            country_code = "IE"
        else:
            country_code = "GB"

        try:
            phone, hours_of_operation = get_additional(page_url)
        except:
            phone, hours_of_operation = SgRecord.MISSING, SgRecord.MISSING

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
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.energiefitness.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
