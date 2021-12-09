import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def clean_phone(line):
    if "," in line:
        line = line.split(",")[0].strip()

    if "(" in line:
        _tmp = []
        for l in line:
            if l.isdigit() and len(_tmp) != 10:
                _tmp.append(l)

        if len(_tmp) < 10:
            return "<MISSING>"

        _tmp.insert(3, "-")
        _tmp.insert(7, "-")
        line = "".join(_tmp)

    return line


def clean_hours(line):
    line = line.replace("Main Clinic Facility:;300 Birnie Avenue Springfield, MA;", "")
    splitters = [
        "(",
        "We ",
        "Holidays",
        "Times",
        "*",
        "Patient",
        "Open for",
        "Ultrasound",
        "Screenings",
        "Xray",
        "Physical",
    ]
    for s in splitters:
        if s in line:
            line = line.split(s)[0].strip()

    return line


def get_params():
    _types = dict()
    coords = dict()
    r = session.get("https://www.baystatehealth.org/locations", headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'var maplocations=')]/text()"))
    js = json.loads(text.split("var maplocations=")[1])

    for _type, records in js.items():
        for record in records:
            slug = record.get("LocationDetailLink")
            if _types.get(slug) is None:
                _types[slug] = _type
            else:
                _types[slug] = f"{_types[slug]}, {_type}"
            lat = record.get("LocationLat") or SgRecord.MISSING
            lng = record.get("LocationLon") or SgRecord.MISSING
            coords[slug] = (lat, lng)
    return _types, coords


def get_urls():
    urls = []
    for i in range(1, 5000):
        r = session.get(
            f"https://www.baystatehealth.org/locations/search-results?page={i}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        links = tree.xpath(
            "//a[contains(@id, 'main_1_contentpanel_1_lvSearchResults_hlItem_')]/@href"
        )
        urls += links

        if len(links) < 10:
            break

    return urls


def get_data(url, _types, coords, sgw: SgWriter):
    page_url = f"https://www.baystatehealth.org{url}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    if "-" in location_name:
        location_name = location_name.split("-")[0].strip()

    street_address = ", ".join(
        tree.xpath("//span[contains(@class, 'location-address')]/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@class='location-town']/text()")).strip()
    state = "".join(tree.xpath("//span[@class='location-state']/text()")).strip()

    postal = "".join(tree.xpath("//span[@class='location-zip']/text()")).strip()
    phone = (
        "".join(tree.xpath("//span[@class='location-office-phone']/a/text()")).strip()
        or ""
    )

    if phone:
        phone = clean_phone(phone)
    else:
        phone = "".join(
            tree.xpath("//span[@class='location-office-appointment-phone']/text()")
        ).strip()

    latitude, longitude = coords.get(url) or ("<MISSING>", "<MISSING>")
    if latitude == "<MISSING>":
        for k in coords.keys():
            if k in url:
                latitude, longitude = coords[k]
                break
    location_type = _types.get(url)
    hours = tree.xpath(
        "//div[@id='main_2_contentpanel_1_pnlOfficeHours']//text()|//div[@id='main_2_contentpanel_0_pnlOfficeHours']//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))

    if hours:
        hours_of_operation = clean_hours(";".join(hours)) or "<MISSING>"
    else:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    _types, coords = get_params()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {
            executor.submit(get_data, url, _types, coords, sgw): url for url in urls
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.baystatehealth.org/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
