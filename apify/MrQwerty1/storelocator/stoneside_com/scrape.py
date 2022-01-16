import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.stoneside.com/locations")
    tree = html.fromstring(r.text.replace("wicket:id", "wicket"))

    return tree.xpath("//a[@wicket='locationLink']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.stoneside.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text.replace("wicket:id", "wicket"))
    text = "".join(tree.xpath("//script[contains(text(), 'LocalBusiness')]/text()"))
    j = json.loads(text)
    location_name = j.get("name")

    a = j.get("address") or {}
    street_address = ", ".join(
        tree.xpath("//div[contains(@wicket, 'address')]/text()")
    ).strip()
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = h.get("dayOfWeek")
        start = h.get("opens")
        end = h.get("closes")
        _tmp.append(f"{day}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.stoneside.com/"
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
