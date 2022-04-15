from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog

DOMAIN = "torchystacos.com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_hours(url):
    _id = url.split("/")[-2]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    log.info(f"Now Crawling: {url}")
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    hoo = (
        ";".join(
            tree.xpath("//div[@class='show-more']/p[@itemprop='openingHours']/text()")
        )
        or "<MISSING>"
    )

    if tree.xpath("//img[contains(@src, 'coming_soon')]"):
        hoo = "Coming Soon"

    log.info(f"HOO: {hoo}")
    return {_id: hoo}


def fetch_data(sgw):
    urls = []
    hours = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    r = session.get("https://torchystacos.com/locations-json/", headers=headers)
    js = r.json()

    for j in js:
        urls.append("https://torchystacos.com" + j.get("permalink"))

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = "https://torchystacos.com" + j.get("permalink")
        _id = page_url.split("/")[-2]
        location_name = j.get("name")
        street_address = j.get("address") or "<MISSING>"
        if street_address.find("77005") != -1:
            street_address = street_address.split(",")[0]
        city = j.get("city") or "<MISSING>"
        state = j.get("state_abbr") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"

        if location_name.lower().find("coming") == -1:
            hours_of_operation = hours.get(_id)
        else:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://torchystacos.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
