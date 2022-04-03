import json
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://www.avis.co.uk/sitemaps/avis-en_GB.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if "united-kingdom" in link and link.count("/") >= 9:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    source = r.text
    if not source:
        return
    tree = html.fromstring(source)
    text = "".join(tree.xpath("//script[contains(text(), 'AutoRental')]/text()"))
    if not text:
        return
    j = json.loads(text, strict=False)

    location_name = j.get("name")

    try:
        _tmp = []
        line = "".join(tree.xpath("//script[contains(text(), 'carSearchData')]/text()"))
        line = line.split('"OpeningTimes":')[1].split("}],")[0] + "}]"
        js = json.loads(line)
        for s in js:
            day = s.get("DayOfWeek")
            inter = s.get("FirstText")
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)
    except:
        hours = j.get("openingHours") or []
        hours = [" ".join(h.split()) for h in hours]
        hours_of_operation = ";".join(hours) or "Closed"

    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")
    store_number = re.findall(regex, source).pop()

    g = a["addressCountry"].get("geo") or {}
    latitude = g.get("latitude") or ""
    longitude = g.get("longitude") or ""
    if str(latitude) == "0":
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
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
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.avis.co.uk/"
    regex = r'"StationCode":"(.+?)"'
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
