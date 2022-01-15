import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://unclejulios.com/locations/")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[@class='restaurants__sublink']/@href"))


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'ReserveAction')]/text()")
    ).strip()
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress") or ""
    street_address = street_address.replace("Open ", "")
    if "weather" in street_address:
        street_address = street_address.split(".")[-1].strip()
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    phone = j.get("telephone")

    g = j.get("geo")
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    hours = j.get("openingHoursSpecification")

    for h in hours:
        day = h.get("dayOfWeek")
        if type(day) == list:
            day = f"{day[0]} - {day[-1]}"

        start = h.get("opens")
        close = h.get("closes")
        _tmp.append(f"{day}: {start} - {close}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
        phone=phone,
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
    locator_domain = "https://unclejulios.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
