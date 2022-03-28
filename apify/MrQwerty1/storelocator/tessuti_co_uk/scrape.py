import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_urls(driver):
    driver.get("https://www.tessuti.co.uk/store-locator/all-stores/")
    tree = html.fromstring(driver.page_source)

    return tree.xpath("//a[@class='storeCard guest']/@href")


def get_data(slug, driver):
    locator_domain = "https://www.tessuti.co.uk/"

    page_url = f"https://www.tessuti.co.uk{slug}"
    driver.get(page_url)
    tree = html.fromstring(driver.page_source)
    text = "".join(
        tree.xpath("//script[contains(text(), 'openingHoursSpecification')]/text()")
    )
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = page_url.split("/")[-2]
    location_name = j.get("name")

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = h.get("dayOfWeek")
        start = h.get("opens")
        if not start:
            _tmp.append(f"{day}: Closed")
            continue
        end = h.get("closes")
        _tmp.append(f"{day}: {start}-{end}")
    hours_of_operation = ";".join(_tmp)

    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality") or ""
    if "," in city:
        city = city.split(",")[-1].strip()
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone") or ""
    if len(phone) < 7:
        phone = SgRecord.MISSING

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    with SgChrome(is_headless=True) as driver:
        urls = get_urls(driver)
        for url in urls:
            yield get_data(url, driver)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        data = fetch_data()
        for row in data:
            writer.write_row(row)
