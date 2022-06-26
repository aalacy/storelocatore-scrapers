import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def get_js(tree):
    text = "".join(tree.xpath("//script[contains(text(), '.parseJSON(')]/text()"))
    text = text.split(".parseJSON('")[1].split("');")[0]
    js = json.loads(text)

    return js


def get_urls():
    urls = set()
    search = DynamicZipSearch(country_codes=[SearchableCountries.GERMANY])
    for _zip in search:
        api = f"https://www.jet-tankstellen.de/kraftstoff/filialfinder/?location={_zip}&place_id=&feature=&radius=25"
        r = session.get(api, headers=headers)
        tree = html.fromstring(r.text)
        js = get_js(tree)

        if not js:
            search.found_nothing()
            continue

        for j in js:
            lat = j.get("lat")
            lng = j.get("lng")
            search.found_location_at(lat, lng)
            urls.add(j.get("link_1"))

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.jet-tankstellen.de{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    j = get_js(tree)
    location_name = "".join(
        tree.xpath("//h1[@class='d-none d-md-block']/text()")
    ).strip()
    street_address = j.get("street")
    city = j.get("city")
    postal = j.get("postcode")
    country_code = "DE"
    phone = j.get("phone")
    latitude = j.get("lat")
    longitude = j.get("lon")

    hours = tree.xpath(
        "//div[h4[contains(text(), 'Öffnungszeiten')]]/following-sibling::div/p[last()]/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    _types = []
    images = tree.xpath(
        "//h3[contains(text(), 'Service')]/following-sibling::div//img/@src"
    )
    for img in images:
        if "-bistro" in img:
            _types.append("Bistro")
        if "-waeesche" in img:
            _types.append("Jet Wäsche")
        if "-autogas" in img:
            _types.append("Autogas")

    location_type = ";".join(_types)

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
        locator_domain=locator_domain,
        location_type=location_type,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.jet-tankstellen.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
