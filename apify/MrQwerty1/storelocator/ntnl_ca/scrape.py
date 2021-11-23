import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    r = session.get("https://www.ntnl.ca/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'Learn more')]/@href")


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.ntnl.ca{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//div[@data-block-json]/@data-block-json"))
    location_name = "national on " + tree.xpath("//h2/text()")[0].strip()

    j = json.loads(text)["location"]
    if "westhills" in page_url:
        street_address = tree.xpath("//a[contains(@href, '/maps/place')]/text()")[
            0
        ].strip()[:-1]
        line = (
            tree.xpath("//a[contains(@href, '/maps/place')]/text()")[-1]
            .strip()
            .split(", ")
        )
        marker = "".join(tree.xpath("//a[contains(@href, '/maps/place')]/@href"))
        latitude, longitude = get_coords_from_google_url(marker)
    else:
        street_address = j.get("addressLine1")
        line = j.get("addressLine2").split(", ")
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")

    city = line.pop(0).strip()
    state = line.pop(0).strip()
    try:
        postal = line.pop(0).strip()
    except:
        postal = SgRecord.MISSING
    phone = "".join(
        tree.xpath(
            "//p[./strong[contains(text(), 'contact us')]]/a[contains(@href, 'tel:')]/text()"
        )
    ).strip()

    _tmp = []
    days = tree.xpath("//p[./strong[contains(text(), 'hours')]]/strong/text()")[1:]
    times = tree.xpath("//p[./strong[contains(text(), 'hours')]]/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "Temporarily Closed"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="CA",
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
    locator_domain = "https://www.ntnl.ca/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
