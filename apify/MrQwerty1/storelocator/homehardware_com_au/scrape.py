import re
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.homehardware.com.au/stores", headers=headers)
    tree = html.fromstring(r.text)
    script = "".join(
        tree.xpath("//script[contains(text(), 'Magento_Ui/js/core/app')]/text()")
    ).replace("\\", "")
    urls = re.findall(r'"url":"(.+?)"', script)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@class='page-title']//text()"))
    line = tree.xpath("//div[@class='shop-details']//div[@class='address']//text()")
    line = list(filter(None, [li.strip() for li in line]))

    street_address = line.pop(0)
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()
    csz = line.pop(-2)
    city, state, postal = csz.split(", ")
    country_code = "AU"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='shop-details']//div[@class='contact-info']//span//text()"
            )
        )
        .replace("T", "")
        .replace(":", "")
        .strip()
    )
    if "F" in phone:
        phone = phone.split("F")[0].strip()
    store_number = page_url.split("-")[-1]

    try:
        text = "".join(
            tree.xpath("//script[contains(text(), 'viewBanersWrapper')]/text()")
        )
        text = text.split('"markers":[')[1].split(',"closestShops"')[0] + "}"
        g = json.loads(text)
        latitude = g.get("latitude")
        longitude = g.get("longitude")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    try:
        source = "".join(
            tree.xpath("//script[contains(text(), 'smile-storelocator-store')]/text()")
        )
        source = source.split('"openingHours":')[1].split("}]],")[0] + "}]]"
        hours = json.loads(source)
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]

        for day, h in zip(days, hours):
            try:
                start = h[0]["start_time"]
                end = h[0]["end_time"]
            except:
                continue
            _tmp.append(f"{day}: {start}-{end}")
    except:
        pass

    hours_of_operation = ";".join(_tmp)

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
    locator_domain = "https://www.homehardware.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
