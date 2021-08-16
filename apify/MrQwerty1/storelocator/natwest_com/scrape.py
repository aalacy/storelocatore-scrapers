import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_urls():
    r = session.get("https://locator.natwest.com/?")
    tree = html.fromstring(r.text)
    token = "".join(tree.xpath("//input[@id='csrf-token']/@value"))

    data = {
        "CSRFToken": token,
        "lat": "51.5073509",
        "lng": "-0.1277583",
        "site": "Natwest",
        "pageDepth": "4",
        "search_term": "London",
        "searchMiles": "100",
        "offSetMiles": "50",
        "maxMiles": "2000",
        "listSizeInNumbers": "10000",
        "search-type": "1",
    }

    r = session.post(
        "https://locator.natwest.com/content/branchlocator/en/natwest/_jcr_content/content/homepagesearch.search.html",
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class=' results-block real branch']/a[@class='holder']/@href"
    )


def get_data(url, sgw: SgWriter):
    page_url = f"https://locator.natwest.com{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='branchName']/@value"))
    line = tree.xpath("//div[@class='print']//td[@class='first']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = ", ".join(line)
    adr = parse_address(International_Parser(), line)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or SgRecord.MISSING
    )

    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()

    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    if "Juxon House" in street_address:
        street_address = line.split(",")[1].strip()
        postal = line.split(",")[-1].strip()
    country_code = "GB"
    store_number = page_url.split("/")[-1].split("-")[0]

    phone = (
        "".join(tree.xpath("//div[@class='print']//td[./span]/text()")).strip()
        or SgRecord.MISSING
    )
    if phone.find("(") != -1:
        phone = phone.split("(")[0].strip()

    text = "".join(tree.xpath("//script[contains(text(), 'locationObject')]/text()"))
    try:
        text = text.split("locationObject =")[1].split(";")[0].strip()
        js = json.loads(text)
        latitude = js.get("LAT") or SgRecord.MISSING
        longitude = js.get("LNG") or SgRecord.MISSING
        location_type = js.get("TYPE") or SgRecord.MISSING
    except IndexError:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//tr[@class='time']")

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        if t.xpath("./td[@colspan='3']"):
            time = "Closed"
        else:
            time = "".join(t.xpath("./td/text()")[1:]).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING
    if hours_of_operation.lower().count("closed") >= 7:
        hours_of_operation = "Closed"

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
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://natwest.com"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
