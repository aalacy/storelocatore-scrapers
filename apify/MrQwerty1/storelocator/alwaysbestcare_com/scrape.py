from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import sglog


def get_params():
    params = set()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=6
    )

    for _zip in search:
        api = f"https://www.alwaysbestcare.com/wp-json/ral/v1/location/offices?q={_zip}"
        r = session.get(api, headers=headers)
        js = r.json()["features"]
        logger.info(f"{_zip}: {len(js)} location(s) found")

        for j in js:
            p = j.get("properties") or {}
            store_number = p.get("storeid")
            page_url = p.get("url")
            g = j.get("geometry") or {}
            lng, lat = g.get("coordinates") or (SgRecord.MISSING, SgRecord.MISSING)
            params.add((page_url, lat, lng, store_number))

    return params


def get_data(param, sgw: SgWriter):
    page_url, latitude, longitude, store_number = param
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r.status_code}")
    if r.status_code != 200:
        logger.info(f"{page_url} skipped b/c status code is {r.status_code}")
        return
    tree = html.fromstring(r.text)

    try:
        location_name = (
            tree.xpath("//p[span[contains(@itemprop,'streetAddress')]]/text()")[0]
            .replace("|", "")
            .strip()
        )
    except IndexError:
        location_name = SgRecord.MISSING
    street_address = " ".join(
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
    )
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "US"
    phone = "".join(tree.xpath("//h3/a[contains(@href, 'tel:')]/text()")).strip()

    if latitude == SgRecord.MISSING or latitude == 0:
        text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
        if "/@" in text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]

    if latitude == SgRecord.MISSING or str(latitude) == "0":
        latitude, longitude = SgRecord.MISSING

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
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()
    logger.info(f"{len(params)} URLs to scrape")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.alwaysbestcare.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="alwaysbestcare.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
