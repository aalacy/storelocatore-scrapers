import json

from lxml import html
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import sglog
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


def get_urls():
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

    for lat, lng in search:
        data = {"lat": lat, "lng": lng}
        r = session.post(
            "https://www.nandos.co.za/eat/restaurant_search_results",
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        text = "".join(
            tree.xpath(
                "//script[contains(text(), 'window.mapData.items.push(')]/text()"
            )
        )
        if not text:
            search.found_nothing()

        tt = text.split("window.mapData.items.push(")
        tt.pop(0)

        logger.info(f"{(lat, lng)}: {len(tt)}")
        for t in tt:
            j = json.loads(t.split(");")[0])
            slug = j.get("id_name")
            url = f"https://www.nandos.co.za/eat/restaurant/{slug}"
            urls.add(url)
            la = j.get("latitude")
            ln = j.get("longitude")
            search.found_location_at(la, ln)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r}")
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = "".join(tree.xpath("//h1/following-sibling::ul/li[1]//text()"))
    street_address, city, state, postal = get_international(raw_address)
    try:
        phone = tree.xpath(
            "//h1/following-sibling::ul/li/a[contains(@href, 'tel:')]/text()"
        )[0].strip()
    except IndexError:
        phone = SgRecord.MISSING
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
    urls = get_urls()
    logger.info(f"{len(urls)} URLs to crawl")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    logger = sglog.SgLogSetup().get_logger(logger_name="nandos.co.za")
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
