import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import sglog

locator_domain = "natwest.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_urls():
    r = session.get("https://www.natwest.com/locator?")
    tree = html.fromstring(r.text)
    token = "".join(tree.xpath("//input[@id='csrf-token']/@value"))

    data = {
        "CSRFToken": token,
        "lat": "51.5072178",
        "lng": "-0.1275862",
        "site": "Natwest",
        "pageDepth": "4",
        "search_term": "London",
        "searchMiles": "5",
        "offSetMiles": "50",
        "maxMiles": "3000",
        "listSizeInNumbers": "999",
        "search-type": "1",
    }

    r = session.post(
        "https://www.natwest.com/content/branchlocator/en/natwest/_jcr_content/content/homepagesearch.search.html",
        data=data,
    )
    log.info(f"Post Status: {r}")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class=' results-block real branch']/a[@class='holder']/@href"
    )


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.natwest.com{url}"

    r = session.get(page_url)
    log.info(f"Crawling {page_url} and response status: {r}")
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='branchName']/@value"))
    line = tree.xpath("//div[@class='print']//td[@class='first']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    raw_address = ", ".join(line)
    postcode = line.pop()
    ad = ", ".join(line)
    adr = parse_address(International_Parser(), ad)

    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street_address = f"{adr1} {adr2}".strip()

    if len(street_address) < 5:
        street_address = raw_address.split(",")[0].strip()

    city = adr.city or SgRecord.MISSING
    if "Juxon House" in street_address:
        street_address = raw_address.split(",")[1].strip()

    country_code = "GB"
    store_number = page_url.split("/")[-1].split("-")[0]
    phone = "".join(tree.xpath("//div[@class='print']//td[./span]/text()")).strip()
    if "Int'l:" in phone:
        phone = phone.split("Int'l:")[1].replace("(", "").replace(")", "").strip()

    text = "".join(tree.xpath("//script[contains(text(), 'locationObject')]/text()"))
    try:
        text = text.split("locationObject =")[1].split(";")[0].strip()
        js = json.loads(text)
        latitude = js.get("LAT")
        longitude = js.get("LNG")
        location_type = js.get("TYPE")
    except IndexError:
        latitude = SgRecord.MISSING
        longitude = SgRecord.MISSING
        location_type = SgRecord.MISSING

    _tmp = []
    tr = tree.xpath("//tr[@class='time']")

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        if t.xpath("./td[@colspan='3']"):
            time = "Closed"
        else:
            time = "".join(t.xpath("./td/text()")[1:]).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)
    if hours_of_operation.lower().count("closed") >= 7:
        hours_of_operation = "Closed"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postcode,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":

    session = SgRequests(proxy_country="gb")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
