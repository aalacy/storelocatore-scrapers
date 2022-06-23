import json

from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    _tmp = []
    r = session.get(page_url, headers=headers)
    if r.status_code != 200 or len(r.text) < 128:
        return
    tree = html.fromstring(r.text)
    hours = tree.xpath("//div[@class='open-hours__day']")

    for h in hours:
        day = " ".join("".join(h.xpath("./span[1]//text()")).split())
        inter = " ".join("".join(h.xpath("./span[2]//text()")).split())
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.williamhbrown.co.uk/branches/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("""//script[contains(text(), '"branches":')]/text()"""))
    text = text.split('"branches":')[1].split("});")[0]
    js = json.loads(text)

    urls = set()
    for j in js:
        slug = j.get("branch_url")
        urls.add(f"https://www.williamhbrown.co.uk{slug}")

    hoo = dict()
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_hoo, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            key = future_to_url[future].split("/")[-1]
            hoo[key] = future.result()

    for j in js:
        adr = j.get("address") or ""
        raw_address = adr.replace("\n", ", ")
        line = adr.split("\n")
        if "dummy" in line[0] or line[0] == ".":
            continue

        street_address = line.pop(0)
        city = line.pop(0)
        postal = line.pop()
        country_code = "GB"
        store_number = j.get("branch_id")
        location_name = j.get("name")
        slug = j.get("branch_url")
        page_url = f"https://www.williamhbrown.co.uk{slug}"
        key = page_url.split("/")[-1]
        try:
            phone = j["services"][0]["number"]
        except:
            phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = hoo.get(key)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.williamhbrown.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
