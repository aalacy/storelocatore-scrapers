import json
from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.text)


def get_urls():
    tree = get_tree("https://www.brightstarcare.com/about-us/find-a-location")

    return tree.xpath("//section[@class='map-list']//div[@class='row']//a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.brightstarcare.com{slug}"
    tree = get_tree(page_url)
    items = tree.xpath(
        "//section[@class='map-list content-list-container']//div[@class='row']"
    )

    for item in items:
        text = (
            "".join(item.xpath(".//script/text()"))
            .replace("locations.push(", "")
            .replace(");", "")
            .strip()
        )
        a = json.loads(text)
        location_name = "".join(item.xpath(".//h3/text()")).strip()
        page_url = f'https://www.brightstarcare.com{a.get("url")}'
        street_address = a.get("address")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipcode") or ""
        postal = "".join(postal.split())
        phone = "".join(item.xpath(".//span[@class='js-phone']/text()")).strip()
        latitude = a.get("lat")
        longitude = str(a.get("lng")).replace("None", "")
        if "." not in longitude and longitude:
            longitude = longitude[:3] + "." + longitude[3:]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.brightstarcare.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
