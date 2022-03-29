import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_coords_from_text(text):
    latitude = "".join(re.findall(r"lat:(\d{2}.\d+)", text)).strip()
    longitude = "".join(re.findall(r"lng:(-?\d{2,3}.\d+)", text)).strip()
    return latitude, longitude


def get_urls():
    r = session.get("https://merrittclubs.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@class, 'nectar-button') and contains(@href, '/locations/')]/@href"
    )


def get_data(url, sgw: SgWriter):
    page_url = f"https://merrittclubs.com{url}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//span[text()='ADDRESS:']/following-sibling::span/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    phone = "".join(
        tree.xpath("//span[text()='PHONE:']/following-sibling::span/text()")
    ).strip()
    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.Marker(')]/text()")
    )
    text = text.split("new google.maps.Marker(")[1].split("}")[0]
    latitude, longitude = get_coords_from_text(text)
    hours = tree.xpath(
        "//p[./span[text()='STAFFED HOURS:']]/preceding-sibling::p//text()|//span[text()='HOURS:']/following-sibling::span/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
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
    locator_domain = "https://merrittclubs.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
