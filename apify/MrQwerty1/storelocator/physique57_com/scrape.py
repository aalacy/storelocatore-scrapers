import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    country = adr.country or SgRecord.MISSING

    return street, city, state, postal, country


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.content)


def get_urls():
    urls = set()
    tree = get_tree(locator_domain)
    links = tree.xpath(
        "//a[contains(text(), 'Studios')]/following-sibling::ul[1]//a/@href"
    )
    for link in links:
        if (
            "virtual" in link
            or not link.startswith("/")
            or "#" in link
            or "outdoor" in link
        ):
            continue
        urls.add(link)

    return urls


def get_uniq(sgw, tree, page_url):
    text = "".join(tree.xpath(".//div[contains(@id, 'wpgmza_marker_list_')]/@id"))
    key = text.split("wpgmza_marker_list_")[-1]
    r = session.get("https://physique57.com/wp-json/wpgmza/v1/markers", headers=headers)
    js = r.json()
    for j in js:
        _id = j.get("map_id")
        if _id != key:
            continue

        location_name = j.get("title")
        a = j.get("address") or ""
        latitude = j.get("lat")
        longitude = j.get("lng")
        street_address, city, state, postal, country = get_international(a)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def get_data(slug, sgw: SgWriter):
    page_url = f"https://physique57.com{slug}"
    tree = get_tree(page_url)
    text = "".join(
        tree.xpath("//script[contains(text(), 'ExerciseGym')]/text()")
    ).strip()
    if not text:
        get_uniq(sgw, tree, page_url)
        return
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress") or ""
    street_address = street_address.replace("- Dubai", "").strip()
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    phone = j.get("telephone")
    store_number = j.get("branchCode")

    g = j.get("geo")
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    hours = j.get("openingHoursSpecification")
    if isinstance(hours, dict):
        day = hours.get("dayOfWeek") or []
        days = ",".join(day)
        start = hours.get("opens") or ""
        end = hours.get("closes") or ""
        hours_of_operation = f"{days}: {start}-{end}"
    elif isinstance(hours, list):
        _tmp = []
        for h in hours:
            d = h.get("dayOfWeek") or []
            if isinstance(d, str):
                day = d
            else:
                day = ",".join(d)
            start = h.get("opens")
            end = h.get("closes")
            _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)
    else:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://physique57.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
