import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.peachwaveyogurt.com/locations/?q=&search=Search")
    tree = html.fromstring(r.text)

    return tree.xpath("//h2[@class='cms-loc-directory-part-name']/a/@href")


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
        "LandmarkName": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = SgRecord.MISSING
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
    except usaddress.RepeatedLabelError:
        street_address = ",".join(line.split(",")[:3])
        city = line.split(",")[3].strip()
        state = SgRecord.MISSING
        postal = SgRecord.MISSING

    return street_address, city, state, postal


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("-")[0].strip()
    line = tree.xpath("//div[@class='address']/p//text()")
    line = list(filter(None, [l.replace("\xa0", " ").strip() for l in line]))
    if not line:
        return
    if "Coming" in line[0]:
        return

    raw_address = ", ".join(line)
    street_address, city, state, postal = get_address(raw_address)
    if street_address.startswith("Park"):
        street_address = street_address.split(",")[-1].strip()

    country_code = "US"
    if "Cayman" in city:
        country_code = "KY"
    store_number = page_url.split("/")[-1]
    phone = "".join(tree.xpath("//div[@class='phone']/p/text()")).strip()
    if "Coming" in phone:
        return
    if "Located" in phone:
        phone = SgRecord.MISSING

    text = "".join(
        tree.xpath("//script[contains(text(), 'var myLocationMarker')]/text()")
    )
    try:
        text = text.split("new google.maps.LatLng")[1].split(";")[0]
        latitude, longitude = eval(text)
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    _tmp = []
    li = tree.xpath("//div[@class='cms-loc-directory-hours']//li")
    for l in li:
        day = "".join(l.xpath("./span/text()")).strip()
        time = "".join(l.xpath("./text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)
    if tree.xpath("//p[contains(text(), 'Opening')]"):
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.peachwaveyogurt.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
