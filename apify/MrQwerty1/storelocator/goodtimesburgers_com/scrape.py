from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    coords = dict()
    api = "https://api.dineengine.io/goodtimes/custom/dineengine/vendor/olo/restaurants?includePrivate=false"
    r = session.get(api, headers=headers)
    js = r.json()["restaurants"]

    for j in js:
        phone = j.get("telephone") or ""
        key = phone.replace("(", "").replace(")", "").replace(" ", "-")
        lat = j.get("latitude")
        lng = j.get("longitude")
        url = str(j.get("url")).replace("menu", "locations")
        coords[key] = (lat, lng, url)

    return coords


def fetch_data(sgw: SgWriter):
    api = "https://api.dineengine.io/goodtimes/items/custom_pages?fields%5B0%5D=%2A.%2A.%2A.%2A&single=false&limit=-1"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        if j.get("title") == "Find Us":
            source = j.get("content")
            break
    else:
        source = "<html></html>"

    coords = get_coords()
    tree = html.fromstring(source)
    divs = tree.xpath("//li[@class='container']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='h-fit-content']/div[1]/div[1]/text()")
        ).strip()
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()

        street_address = (
            "".join(d.xpath(".//div[@class='h-fit-content']/div[1]/div[2]/text()"))
            .replace(" v ", "")
            .strip()
        )
        csz = (
            "".join(d.xpath(".//div[@class='h-fit-content']/div[1]/div[3]/text()"))
            .strip()
            .split()
        )
        if not csz:
            continue

        postal = csz.pop()
        state = csz.pop()
        city = " ".join(csz)
        latitude, longitude, page_url = coords.get(phone) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        _tmp = []
        hours = d.xpath(
            ".//div[@class='d-grid-locations']/preceding-sibling::div[1]/div/span"
        )
        for h in hours:
            day = "".join(h.xpath("./text()")).strip()
            d = day.lower()
            if "break" in d or "lunch" in d or "lobby" in d:
                break
            inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
            _tmp.append(f"{day} {inter}")

        hours_of_operation = ";".join(_tmp)

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://goodtimesburgers.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "X-Device-Id": "7ce71050-5d71-4f10-bbff-eb5b2ae062ea",
        "Origin": "https://goodtimesburgers.com",
        "Connection": "keep-alive",
        "Referer": "https://goodtimesburgers.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
