from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://locations.jollibeeusa.com/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 5:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url + ".json")
    j = r.json()["profile"]
    a = j.get("address") or {}

    try:
        location_name = j["c_heroSection"]["storeName"]
    except:
        location_name = j.get("name")
    street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")
    country_code = a.get("countryCode")
    try:
        phone = j["mainPhone"]["display"]
    except KeyError:
        phone = SgRecord.MISSING

    latitude = j["yextDisplayCoordinate"]["lat"]
    longitude = j["yextDisplayCoordinate"]["long"]

    _tmp = []
    try:
        hours = j["hours"]["normalHours"]
    except KeyError:
        hours = []

    for h in hours:
        day = h.get("day")
        if h.get("isClosed"):
            _tmp.append(f"{day}: Closed")
        else:
            start = str(h["intervals"][0]["start"])
            end = str(h["intervals"][0]["end"])
            if len(start) == 3:
                start = f"0{start}"
            _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
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
    locator_domain = "https://jollibeeusa.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
