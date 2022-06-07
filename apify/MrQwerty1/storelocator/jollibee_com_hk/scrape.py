from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    coords = dict()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    areas = tree.xpath("//select[@id='area-selection']/option/@value")
    text = "".join(
        tree.xpath("//script[contains(text(), 'store_position[')]/text()")
    ).split("store_position[")
    text.pop(0)
    for t in text:
        if "lat:" not in t:
            continue
        key = t.split("]")[0]
        lat = t.split("lat:")[1].split(",")[0].strip()
        lng = t.split("lng:")[1].split("}")[0].strip()
        coords[key] = (lat, lng)

    return areas, coords


def get_data(area, coords, sgw: SgWriter):
    data = {"area_name": area, "lang": "en", "action": "getStoreLocations"}

    r = session.post(
        "https://jollibee.com.hk/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    try:
        tree = html.fromstring(r.text)
    except:
        return
    divs = tree.xpath("//td[./span[@class='style6']]")

    for d in divs:
        store_number = (
            "".join(d.xpath("./@onclick")).replace("focusStore(", "").replace(")", "")
        )
        location_name = "".join(d.xpath(".//strong/text()")).strip()
        lines = d.xpath(".//text()")
        lines = list(filter(None, [l.strip() for l in lines]))
        lines.pop(0)
        phone = lines.pop().replace("Tel:", "").strip()
        raw_address = lines.pop()
        street_address, city, state, postal = get_international(raw_address)
        latitude, longitude = coords.get(store_number)
        hours_of_operation = SgRecord.MISSING
        if "soon" in location_name.lower():
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="HK",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    areas, coords = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {
            executor.submit(get_data, area, coords, sgw): area for area in areas
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://jollibee.com.hk/"
    page_url = "https://jollibee.com.hk/store-locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jollibee.com.hk",
        "Alt-Used": "jollibee.com.hk",
        "Connection": "keep-alive",
        "Referer": "https://jollibee.com.hk/store-locator/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
