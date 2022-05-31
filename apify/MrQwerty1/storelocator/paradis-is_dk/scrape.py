import re
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.content)


def get_urls():
    coord = dict()
    tree = get_tree("https://paradis-is.dk/butikker/")
    text = "".join(tree.xpath("//script[contains(text(), 'FWP_JSON')]/text()"))
    text = text.split("FWP_JSON =")[1].split("}};")[0] + "}}"
    js = json.loads(text)["preload_data"]["settings"]["map"]["locations"]
    for j in js:
        p = j.get("position") or {}
        lat = p.get("lat") or SgRecord.MISSING
        lng = p.get("lng") or SgRecord.MISSING
        source = j.get("content") or "<html/>"
        root = html.fromstring(source)
        key = "".join(root.xpath("//a/@href")).split("/")[-2]
        coord[key] = (lat, lng)

    return tree.xpath("//div[@class='flex-cols']//a/@href"), coord


def get_data(page_url, sgw: SgWriter):
    tree = get_tree(page_url)

    location_name = " ".join(
        " ".join(tree.xpath("//div[@class='title-info']/h1/text()")).split()
    )
    raw_address = "".join(tree.xpath("//h1/following-sibling::p[1]/text()")).strip()

    try:
        postal = re.findall(r"\d{4}", raw_address).pop()
        street_address = raw_address.split(postal)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address.split(postal)[-1].strip()
    except:
        postal = SgRecord.MISSING
        street_address, city = raw_address.split(", ")

    key = page_url.split("/")[-2]
    latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

    _tmp = []
    hours = tree.xpath("//div[@class='opening-hours']//tr")
    for h in hours:
        line = " ".join(" ".join(h.xpath(".//text()")).split())
        _tmp.append(line)

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="DK",
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://paradis-is.dk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    urls, coords = get_urls()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
