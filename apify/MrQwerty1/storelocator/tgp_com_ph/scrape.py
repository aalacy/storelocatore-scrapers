import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    part = line.split()[-1]
    if part.isdigit():
        adr = parse_address(International_Parser(), line, postcode=part)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://tgp.com.ph/wp-admin/admin-ajax.php"
    r = session.post(api, headers=headers, data=data)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations')]/text()"))
    text = text.split('"locations":')[1].split(',"unit"')[0]
    js = json.loads(text)

    for j in js:
        source = j.get("infowindow") or "<html/>"
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        raw_address = "".join(
            d.xpath(".//p[@class='info-window-address']//text()")
        ).strip()
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(d.xpath(".//p[./i[contains(@class, 'phone')]]/text()")).strip()
        if ";" in phone:
            phone = phone.split(";")[0].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PH",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://tgp.com.ph/"
    page_url = "https://tgp.com.ph/branches/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://tgp.com.ph/branches/",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://tgp.com.ph",
        "Alt-Used": "tgp.com.ph",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "store_locatore_search_lat": "14.4976517",
        "store_locatore_search_lng": "121.0355912",
        "store_locatore_search_radius": "5000",
        "store_locator_category": "",
        "map_id": "997",
        "action": "make_search_request_custom_maps",
        "lat": "14.4976517",
        "lng": "121.0355912",
    }

    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
