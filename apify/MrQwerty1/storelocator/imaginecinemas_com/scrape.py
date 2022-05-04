import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    coord = dict()
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)
    url = tree.xpath("//li[@data-url]/@data-url")
    text = "".join(tree.xpath("//script[contains(text(), 'theatreLocations')]/text()"))
    text = text.split('"theatreLocations":')[1].split("}]};")[0] + "}]"
    js = json.loads(text)
    for j in js:
        _id = j.get("code")
        lat = j.get("latitude")
        lng = j.get("longitude")
        coord[_id] = (lat, lng)

    return url, coord


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//address/strong/text()")).strip()
    line = tree.xpath("//address/text()")
    line = list(filter(None, [" ".join(li.split()) for li in line]))
    raw_address = ", ".join(line)
    street_address = line.pop(0)
    csz = line.pop()
    city = csz.split(", ")[0]
    sz = csz.split(", ")[1]
    state = sz.split()[0]
    postal = sz.replace(state, "").strip()
    country_code = "CA"
    phone = "".join(
        tree.xpath(
            "//strong[contains(text(), 'Office')]/following-sibling::span[1]/text()"
        )
    ).strip()
    key = page_url.split("/")[-2]
    store_number = "".join(tree.xpath(f"//li[contains(@data-url, '{key}')]/@data-code"))
    latitude, longitude = coords.get(store_number)
    hours = tree.xpath(
        "//strong[contains(text(), 'Hours')]/following-sibling::span/text()"
    )
    hours = list(filter(None, [" ".join(h.split()) for h in hours]))
    hours_of_operation = ";".join(hours)
    if "2022" in hours_of_operation:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://imaginecinemas.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    urls, coords = get_params()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
