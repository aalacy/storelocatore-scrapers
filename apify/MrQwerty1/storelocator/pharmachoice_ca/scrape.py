from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    if (len(postal) < 6 or postal == SgRecord.MISSING) and line:
        postal = " ".join(line.split()[-2:])

    return street, city, state, postal


def get_urls():
    urls = set()
    data = {
        "num": "1000",
        "swLat": "34.18787940403334",
        "swLng": "-145.30983159207807",
        "neLat": "59.88394813122903",
        "neLng": "-45.85505319317005",
        "action": "w2mb_get_map_markers",
        "without_listings": "1",
    }
    r = session.post("https://www.pharmachoice.com/wp-admin/admin-ajax.php", data=data)
    js = r.json()["map_markers"]

    for j in js:
        if isinstance(j, list):
            source = j[-1]
        else:
            continue
        tree = html.fromstring(source)
        urls.add(tree.xpath("//a[contains(@href, 'locations')]/@href")[0])

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    logger.info(f"{page_url}: respone {r.status_code}")
    if r.status_code != 200:
        return
    if "pharmachoice.com" not in str(r.url):
        logger.info(f"{page_url} redirects to {r.url}")
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    raw_address = " ".join(
        " ".join(tree.xpath("//div[@class='wpsl-location-address1']/text()")).split()
    )
    raw_address = (
        raw_address.replace(";", "").replace("&#39", "'").replace("'", ",").strip()
    )
    street_address, city, state, postal = get_international(raw_address)
    phone = "".join(tree.xpath("//span[@class='phoneNumber']/text()")).strip()
    if "/" in phone:
        phone = phone.split("/")[0].strip()

    if "TBD" in phone:
        phone = SgRecord.MISSING

    text = "".join(tree.xpath("//a[contains(@href, 'daddr=')]/@href"))
    try:
        latitude, longitude = text.split("&daddr=")[1].split(",")
        if latitude == "0":
            raise IndexError
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[@class='wpsl-locations-details3']/span")
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        if "closed" in inter.lower():
            inter = "Closed"
        if ";" in inter:
            inter = inter.split(";")[0]
        if not inter:
            continue
        _tmp.append(f"{day} {inter}")

    hours_of_operation = ";".join(_tmp)
    if "TBD" in hours_of_operation:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="CA",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = list(get_urls())
    logger.info(f"{len(urls)} URLs were found")

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.pharmachoice.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="pharmachoice.com")
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
