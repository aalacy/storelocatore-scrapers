import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//h1[contains(text(), 'LOCATION')]/following-sibling::h3/a/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.brownscrafthouse.com{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-block-json]/@data-block-json"))
    j = json.loads(text)["location"]

    location_name = tree.xpath("//h1/text()")[0].strip()
    street_address = j.get("addressLine1") or ""
    csz = j.get("addressLine2") or ""
    city, state, postal = csz.split(", ")
    country_code = "CA"
    phone = tree.xpath("//h2//text()")[-1].strip()
    latitude = j.get("markerLat")
    longitude = j.get("markerLng")

    hours = tree.xpath("//h3[contains(text(), 'Hours')]/following-sibling::p//text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)
    if ";Brunch" in hours_of_operation:
        hours_of_operation = hours_of_operation.split(";Brunch")[0]

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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.brownscrafthouse.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
