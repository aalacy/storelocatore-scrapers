import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.boydautobody.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col-xs-4']/a/@href")


def get_data(api, sgw: SgWriter):
    if api.startswith("/locations/"):
        api = f"https://www.boydautobody.com{api}"
    else:
        return
    r = session.get(api)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'values:')]/text()"))
    text = text.split("values:")[1].split("events:")[0].strip()[:-1]
    js = json5.loads(text)

    for j in js:
        j = j.get("data") or {}
        location_name = j.get("fullname")
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country = j.get("country")
        if country == "CAN":
            country = "CA"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        slug = j.get("aliasurl") or ""
        page_url = f"https://www.boydautobody.com{slug}"

        _tmp = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        t = j.get("hoursstruct") or "[]"
        hours = json5.loads(t)
        cnt = 0
        for h in hours:
            day = days[cnt]
            cnt += 1
            if h.get("ISCLOSED"):
                _tmp.append(f"{day}: Closed")
                continue
            start = "".join(h.get("START") or [])
            end = "".join(h.get("END") or [])
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.boydautobody.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
