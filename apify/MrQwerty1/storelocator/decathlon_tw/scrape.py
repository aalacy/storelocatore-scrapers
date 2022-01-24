from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
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


def fetch_data(sgw: SgWriter):
    api = "https://www.decathlon.tw/en/decathlon/store/getstoresintaiwan/"
    r = session.post(api, headers=headers, data=data)
    js = r.json()

    for j in js:
        location_name = j.get("name") or ""
        slug = j.get("identifier") or ""
        page_url = f'https://www.decathlon.tw/en/decathlon/store/detail/{slug.replace("_", "-")}'
        raw_address = j.get("address") or ""
        raw_address = raw_address.replace("<br>", "").strip()
        street_address, city, state, postal = get_international(raw_address)

        phone = j.get("tel_number")
        geo = j.get("location_info") or ","
        latitude, longitude = geo.split(",")
        store_number = j.get("number")

        _tmp = []
        source = j.get("store_opening_hours") or "<html></html>"
        tree = html.fromstring(source)
        text = tree.xpath("//text()")
        for t in text:
            if not t.strip() or "★" in t:
                continue
            _tmp.append(t.strip())

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.endswith(")"):
            hours_of_operation = hours_of_operation.split("(")[0].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name.strip(),
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="TW",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.tw/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "X-Prototype-Version": "1.7",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.decathlon.tw",
        "Connection": "keep-alive",
        "Referer": "https://www.decathlon.tw/en/decathlon/store/search/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {"city_id": "518", "is_province": "1"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
