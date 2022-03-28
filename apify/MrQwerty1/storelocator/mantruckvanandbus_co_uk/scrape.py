import json
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgselenium import SgChrome

agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"


def get_urls(driver):
    driver.get("https://www.mantruckvanandbus.co.uk/dealer-locator/")
    tree = html.fromstring(driver.page_source)

    return tree.xpath("//a[contains(text(), 'Details')]/@href")


def get_data(slug: str, driver: SgChrome):
    locator_domain = "https://www.mantruckvanandbus.co.uk/"
    page_url = f"https://www.mantruckvanandbus.co.uk{slug}"
    driver.get(page_url)
    tree = html.fromstring(driver.page_source)
    text = "".join(tree.xpath("//script[contains(text(), 'AutoDealer')]/text()"))
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = page_url.split("/")[-3]
    location_name = j.get("name")

    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Hours')]/following-sibling::div//tr[not(.//strong)]"
    )
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        inter = "".join(h.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

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
    with SgChrome(is_headless=True, user_agent=agent) as driver:
        urls = get_urls(driver)
        time.sleep(5)

        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_to_url = {
                executor.submit(get_data, url, driver): url for url in urls
            }
            for future in futures.as_completed(future_to_url):
                yield future.result()


if __name__ == "__main__":
    data = fetch_data()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)
