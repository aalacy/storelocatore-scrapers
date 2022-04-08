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
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_urls():
    urls = set()

    for i in range(1, 100):
        r = session.get(f"https://www.pharmachoice.com/w2mb_listing-sitemap{i}.xml")
        tree = html.fromstring(r.content)
        links = tree.xpath("//loc/text()")
        for link in links:
            if link.endswith("/locations/"):
                continue
            urls.add(link)

        if len(links) < 200:
            break

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    if r.status_code != 200:
        return
    if "pharmachoice.com" not in str(r.url):
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    raw_address = " ".join(
        " ".join(tree.xpath("//div[@class='wpsl-location-address1']/text()")).split()
    )
    raw_address = raw_address.replace(";", "").replace("&#39", "'").replace("'", ",")
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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.pharmachoice.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
