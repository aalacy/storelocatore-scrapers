import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.trejostacos.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@href, 'locations')]/following-sibling::span/a/@href"
    )


def get_data(page_url, sgw: SgWriter):
    if page_url.startswith("/"):
        page_url = f"https://www.trejostacos.com{page_url}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    j = json.loads(tree.xpath("//div[@data-block-json]/@data-block-json")[0])[
        "location"
    ]
    location_name = tree.xpath("//title/text()")[0].strip()
    line = tree.xpath("//h2/a[not(contains(@href, 'tel'))]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return
    if "Located" in line[0]:
        line.pop(0)

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    try:
        phone = (
            tree.xpath(
                "//h2/a[contains(@href, 'tel')]/@href|//h2[./a[contains(@href, 'google.com')]]/text()"
            )[0]
            .replace("tel:", "")
            .strip()
        )
        if phone == "(":
            phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/@href")).replace(
                "tel:", ""
            )
    except IndexError:
        phone = SgRecord.MISSING
    latitude = j.get("markerLat")
    longitude = j.get("markerLng")

    _tmp = []
    lines = tree.xpath("//h2/text()")
    for line in lines:
        if "TRE" in line or not line.strip() or "(" in line:
            continue
        _tmp.append(line.strip())

    hours_of_operation = " ".join(_tmp).replace("PM ", "PM;")

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
    locator_domain = "https://www.trejostacos.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
