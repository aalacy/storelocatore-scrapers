from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    text = " ".join(line.split()[-2:])
    for t in text:
        if t.isdigit() and len(text) <= 8:
            ispostal = True
            break
    else:
        ispostal = False
    if ispostal:
        adr = parse_address(International_Parser(), line, postcode=text)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    postal = adr.postcode or ""

    return street_address, city, postal


def get_params():
    params = []
    r = session.get(
        "https://www.energiefitness.com/bin/public/energie-fitness/consumer/gyms/getGymInfo"
    )
    js = r.json()
    for j in js:
        slug = j.get("href")
        lat = j.get("latitude")
        lng = j.get("longitude")
        params.append((slug, (lat, lng)))

    return params


def get_data(param, sgw: SgWriter):
    slug, coords = param
    latitude, longitude = coords
    page_url = f"https://www.energiefitness.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    raw_address = " ".join(
        " ".join(
            tree.xpath(
                "//h3[contains(text(), 'Address') or contains(text(), 'ADDRESS')]/following-sibling::div[1]//p/text()"
            )
        ).split()
    )
    street_address, city, postal = get_international(raw_address)
    if len(street_address) < 5:
        street_address = raw_address.split(",")[0].strip()
    if "," in postal:
        postal = postal.split(",")[-1].strip()
    phone = "".join(
        tree.xpath("//span[@class='info']/a[contains(@href, 'tel:')]/text()")
    ).strip()

    _tmp = []
    hours = tree.xpath("//div[@class='hours-details']/p")
    for h in hours:
        line = " ".join("".join(h.xpath(".//text()")).split())
        if "Hours" in line:
            continue
        if "bank" in line.lower() and "sun" not in line.lower() or "Staffed" in line:
            break
        _tmp.append(line)
        if "sun" in line.lower() or "open" in line.lower():
            break

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.energiefitness.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
