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
    r = session.get("https://www.rbs.co.uk/locator?.html")
    tree = html.fromstring(r.text)
    token = "".join(tree.xpath("//input[@id='csrf-token']/@value"))

    data = {
        "CSRFToken": token,
        "lat": "51.5073509",
        "lng": "-0.1277583",
        "site": "RBS",
        "pageDepth": "4",
        "search_term": "London",
        "searchMiles": "100",
        "offSetMiles": "50",
        "maxMiles": "2000",
        "listSizeInNumbers": "999",
        "search-type": "1",
    }

    r = session.post(
        "https://www.rbs.co.uk/content/branchlocator/en/rbs/_jcr_content/content/homepagesearch.search.html",
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class=' results-block real branch']/a[@class='holder']/@href"
    )


def get_data(url, sgw: SgWriter):
    page_url = f"https://rbs.co.uk{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='branchName']/@value"))
    if location_name.find("(") != -1:
        location_name = location_name.split("(")[0].strip()
    line = tree.xpath("//div[@class='print']//td[@class='first']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    postal = line[-1]
    raw_address = ", ".join(line[:-1])
    adr = parse_address(International_Parser(), raw_address, postcode=postal)

    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()

    city = adr.city
    state = adr.state
    postal = adr.postcode
    country_code = "GB"
    store_number = page_url.split("/")[-1].split("-")[0]

    phone = "".join(tree.xpath("//div[@class='print']//td[./span]/text()")).strip()
    if phone.find("(") != -1:
        phone = phone.split("(")[0].strip()

    text = "".join(tree.xpath("//script[contains(text(), 'locationObject')]/text()"))
    text = text.split("locationObject =")[1].split(";")[0].strip()
    js = json.loads(text)
    latitude = js.get("LAT")
    longitude = js.get("LNG")
    location_type = js.get("TYPE")

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
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://holtsmilitarybanking.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
