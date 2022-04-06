from lxml import html
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
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


def get_urls(coords):
    lat, lng = coords
    data = {"lat": lat, "lng": lng}
    r = session.post(
        "https://www.nandos.co.za/eat/restaurant_search_results",
        headers=headers,
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//section[@id='results-list']/div/a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.nandos.co.za{slug}"
    r = session.get(page_url, headers=headers)
    if r.status_code == 404:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = "".join(tree.xpath("//h1/following-sibling::ul/li[1]//text()"))
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(
        tree.xpath("//h1/following-sibling::ul/li/a[contains(@href, 'tel:')]/text()")
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng"))
    hours_of_operation = ";".join(
        tree.xpath("//h3[contains(text(), 'Opening')]/following-sibling::ul/li/text()")
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="ZA",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = set()
    countries = [
        SearchableCountries.SOUTH_AFRICA,
        SearchableCountries.BOTSWANA,
        SearchableCountries.NAMIBIA,
        SearchableCountries.SWAZILAND,
    ]
    search = DynamicGeoSearch(
        country_codes=countries,
        expected_search_radius_miles=200,
    )
    for p in search:
        for u in get_urls(p):
            urls.add(u)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.nandos.co.za/"
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
