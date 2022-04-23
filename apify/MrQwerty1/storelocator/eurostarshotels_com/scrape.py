import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_urls():
    urls = []
    r = session.get(
        "https://www.eurostarshotels.com/catalogo_hoteles.html", headers=headers
    )
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), '.engine_sygy_data = ')]/text()")
    )
    text = text.split('"hotels":')[1].split(',"cities"')[0]
    js = json5.loads(text)

    for j in js:
        urls.append(j.get("slug"))

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        logger.info(f"{page_url}: {r.status_code}")
        return
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'window.dataSeo')]/text()"))
    text = text.split("hotel    :")[1].split("opinions")[0].strip()[:-1]
    j = json5.loads(text)

    location_name = j.get("name")
    street_address = j.get("address")
    city = j.get("city")
    postal = j.get("cp")
    country_code = j.get("country")
    phone = j.get("tel")
    store_number = j.get("id")
    location_type = j.get("marca")

    g = j.get("coord") or {}
    latitude = g.get("lat")
    longitude = g.get("log")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.eurostarshotels.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="eurostarshotels")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
