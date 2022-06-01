import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://surgefun.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return set(tree.xpath('//a[.//span[text()="LEARN MORE"]]/@href'))


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
        "LandmarkName": "address1",
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
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_id(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath('//script[contains(text(), "const loc=")]/text()'))
    _id = text.split("const loc=")[1].split(";")[0].strip()
    return _id


def get_uniq(page_url, store_number, sgw):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    slug = page_url.split("/")[-2]
    names = tree.xpath(f"//a[contains(@href, '{slug}')]/span/text()")
    names = list(filter(None, [n.strip() for n in names]))
    location_name = names.pop()
    location_type = SgRecord.MISSING
    if "Adventure" in names.pop():
        location_type = "Adventure Park"
        location_name = location_name.replace(location_type, "").strip()
    raw_address = "".join(
        tree.xpath(
            "//span[./i[@class='fas fa-map-marker']]/following-sibling::span/text()"
        )
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    country_code = "US"
    phone = "".join(
        tree.xpath("//span[./i[@class='fas fa-phone']]/following-sibling::span/text()")
    ).strip()

    _tmp = []
    hours = tree.xpath(
        "//h3[./strong[contains(text(), 'Hours')]]/following-sibling::p/strong"
    )
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
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
        country_code=country_code,
        store_number=store_number,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def get_data(page_url, sgw: SgWriter):
    store_number = get_id(page_url)
    api = f"https://plondex.com/wp/jsonquery/loadloc/9/{store_number}"
    r = session.get(api, headers=headers)
    try:
        tree = html.fromstring(r.text)
    except:
        get_uniq(page_url, store_number, sgw)
        return

    location_name = "".join(tree.xpath("//h4[@class='mb-4']/text()")).strip()
    location_type = SgRecord.MISSING
    if "(" in location_name:
        location_type = location_name.split("(")[1].replace(")", "").strip()
        location_name = location_name.split("(")[0].strip()
    raw_address = "".join(
        tree.xpath("//i[@class='fas fa-map-marker']/following-sibling::text()[1]")
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    country_code = "US"
    phone = "".join(
        tree.xpath("//i[@class='fas fa-phone']/following-sibling::text()[1]")
    ).strip()

    _tmp = []
    hours = tree.xpath("//h4[contains(text(), 'Hours')]/following-sibling::b")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
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
        country_code=country_code,
        store_number=store_number,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
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
    locator_domain = "https://surgefun.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
