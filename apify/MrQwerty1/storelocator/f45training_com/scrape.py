import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests, SgRequestError
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_country(line):
    adr = parse_address(International_Parser(), line)
    return adr.country


def get_city(line):
    adr = parse_address(International_Parser(), line)
    return adr.city


def get_phone(url):
    r = session.get(url, headers=headers)
    if isinstance(r, SgRequestError):
        return ""
    tree = html.fromstring(r.text)
    try:
        phone = (
            tree.xpath("//a[contains(@href, 'tel:')]/text()")[0]
            .replace("–", "")
            .strip()
        )
    except IndexError:
        phone = SgRecord.MISSING
    return phone


def fetch_data(sgw: SgWriter):
    phones = dict()
    api = "https://f45training.com/find-a-studio/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'window.studios ')]/text()"))
    text = text.split('"hits":')[1].split("};")[0]
    js = json.loads(text)

    urls = []
    for j in js:
        url = f'{locator_domain}{j.get("slug")}'
        urls.append(url)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_phone, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            phone = future.result()
            key = future_to_url[future].split("/")[-1]
            phones[key] = phone

    for j in js:
        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"{locator_domain}{slug}"
        raw_address = j.get("location")
        street_address, city, state, postal = get_international(raw_address)
        for letter in city:
            if letter.isdigit():
                city = SgRecord.MISSING
                break

        country = j.get("country") or get_country(raw_address)
        if not country:
            if "Korea" in raw_address:
                country = "Korea"
            else:
                country = "United States"

        phone = phones.get(slug)
        g = j.get("_geoloc") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")
        store_number = j.get("objectID")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://f45training.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
