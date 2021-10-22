import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_urls(lat, lng):
    urls = set()
    api_url = "https://heronfoods.com/index.php"

    data = {
        "params": "eyJyZXN1bHRfcGFnZSI6InN0b3JlbG9jYXRvciJ9",
        "ACT": "29",
        "site_id": "1",
        "distance:from": f"{lat}|{lng}",
    }

    r = session.post(api_url, data=data)
    u = r.url

    for i in range(0, 60000, 6):
        url = f"{u}/P{i}"
        r = session.get(url)
        try:
            tree = html.fromstring(r.text.replace("<!--p>", "").replace("</p-->", ""))
        except:
            continue
        divs = tree.xpath("//div[contains(@class, 'box2col store-details-container')]")
        for d in divs:
            page_url = "".join(
                d.xpath(".//a[contains(@href, '/store-details/')]/@href")
            )
            urls.add(page_url)

        if len(divs) < 6:
            break

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@class='box2col store-details']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = " ".join(line)
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode
    country_code = "GB"

    text = "".join(tree.xpath("//div[@class='box-wrapper']//script/text()"))
    latitude = "".join(re.findall(r'"lat":"(\d+.\d+)', text)) or "<MISSING>"
    longitude = "".join(re.findall(r'"lng":"(-?\d+.\d+)', text)) or "<MISSING>"

    _tmp = []
    li = tree.xpath("//div[@class='box2col opening-hours']//li")
    for l in li:
        day = "".join(l.xpath("./text()|./strong/text()")).strip()
        time = "".join(l.xpath("./span/text()|./strong/span/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    iscoming = tree.xpath("//p[@class='new-store']")
    if iscoming:
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = set()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=200,
        expected_search_radius_miles=15,
    )

    for lat, lng in search:
        links = get_urls(lat, lng)
        for link in links:
            urls.add(link)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://heronfoods.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
