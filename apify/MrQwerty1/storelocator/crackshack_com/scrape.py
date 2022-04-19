import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.crackshack.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='cs-black-button' and not(contains(@href, 'coming-soon'))]/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    line = tree.xpath("//p[text()='Address']/following-sibling::p[1]/text()")
    line = list(
        filter(None, [l.replace("Westfield Mall L1", " ").strip() for l in line])
    )
    raw_address = ", ".join(line)
    if "OPENING" in raw_address:
        return

    street_address = line.pop(0)
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()

    postal = re.findall(r"\d{5}", raw_address).pop()
    cs = line.pop().replace(postal, "").strip()
    city, state = cs.split(", ")
    country_code = "US"
    phone = "".join(
        tree.xpath("//p[text()='Phone']/following-sibling::p[1]/text()")
    ).strip()
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]

    _tmp = []
    hours = tree.xpath("//p[text()='Hours']/following-sibling::p[1]/text()")
    for h in hours:
        if not h.strip() or "indoor" in h or "*" in h or "takeout" in h:
            continue
        _tmp.append(h.strip())

    hours_of_operation = ";".join(_tmp)

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
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.crackshack.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
