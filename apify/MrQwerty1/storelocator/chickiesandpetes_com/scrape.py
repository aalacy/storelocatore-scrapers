import re
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_params():
    params = []
    r = session.get("https://chickiesandpetes.com/location/", headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='info']")
    for d in divs:
        url = "".join(d.xpath("./h2/a/@href"))
        raw = "".join(d.xpath("./p[last()]/text()")).strip()
        params.append((url, raw))

    return params


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    adr1 = a.get("address1") or ""
    adr2 = a.get("address2") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city") or ""
    state = a.get("state")
    postal = a.get("postal")
    if not street_address:
        street_address = line.split(city)[0].strip()

    return street_address, city, state, postal


def get_coords_from_text(text):
    latitude = "".join(re.findall(r'"latitude":(\d{2}.\d+)', text)).strip()
    longitude = "".join(re.findall(r'"longitude":(-?\d{2,3}.\d+)', text)).strip()

    return latitude, longitude


def get_exception_locations(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-widget_type='google_maps.default']")

    _tmp = []
    hours = tree.xpath("//h2[./strong[contains(text(), 'Wildwood')]]/text()")
    for h in hours:
        for _t in h.split("\n"):
            if not _t.strip() or "Hours" in _t:
                continue
            _tmp.append(_t.strip())

    for d in divs:
        raw_address = "".join(d.xpath(".//iframe/@title"))
        street_address, city, state, postal = get_address(raw_address)
        location_name = city

        phone = "".join(d.xpath("./following-sibling::div[2]//text()")).strip()

        hours_of_operation = SgRecord.MISSING
        if city == "Wildwood":
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


def get_data(param, sgw: SgWriter):
    page_url, raw_address = param
    if "coming-soon" in page_url:
        return
    if "locations" in page_url:
        get_exception_locations(page_url, sgw)
        return

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    if raw_address[0].isalpha():
        raw_address = "".join(tree.xpath("//iframe[contains(@src, 'google')]/@title"))

    street_address, city, state, postal = get_address(raw_address)
    phone = "".join(
        tree.xpath(
            "//div[./div/h3[contains(text(), 'Phone')]]/following-sibling::div[1]//p//text()"
        )
    ).strip()
    if not phone:
        try:
            line = "".join(tree.xpath("//div[@class='wpsl-location-phone']/p/text()"))
            phone = line.split("Term C:")[1].split("Term")[0].strip()
        except:
            pass
    text = "".join(tree.xpath("//script[contains(text(), 'latitude')]/text()"))
    latitude, longitude = get_coords_from_text(text)

    _tmp = []
    hours = tree.xpath(
        "//div[./div/h3[contains(text(), 'Hours')]]/following-sibling::div[1]//p//text()"
    )
    for h in hours:
        if not h.strip() or "event" in h.lower():
            continue
        if "last" in h.lower():
            break
        if "(" in h:
            h = h.split("(")[0]
        _tmp.append(h.replace("|", " ").strip())
    hours_of_operation = " ".join(_tmp).replace("Hours:", "").strip()

    if not hours_of_operation:
        try:
            line = "".join(
                tree.xpath("//div[@class='wpsl-location-additionalinfo']/p/text()")
            )
            hours_of_operation = line.split("Terminal C:")[1].split("-")[0].strip()
        except:
            pass

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
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://chickiesandpetes.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Alt-Used": "chickiesandpetes.com",
        "Connection": "keep-alive",
        "Referer": "https://chickiesandpetes.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
