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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!4d")[1].strip().split("!")[0].strip()
        if "?" in longitude:
            longitude = longitude.split("?")[0]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_urls():
    r = session.get("https://www.paultaiwan.com/paulstorelocations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//strong/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath("//h2[@class='entry-title']/text()"))
        .replace(" store", "")
        .strip()
    )
    lines = tree.xpath("//blockquote/p/text()")
    phone = lines.pop(0)
    lines.pop(0)

    i = 0
    for line in lines:
        if "hours" in line:
            break
        i += 1

    raw_address = " ".join(lines[:i])
    street_address, city, state, postal = get_international(raw_address)
    if city == "City":
        city = street_address.split()[-1] + " City"
        street_address = " ".join(street_address.split()[:-1])

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude, longitude = get_coords_from_embed(text)
    hours_of_operation = ";".join(lines[i + 1 :])

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="TW",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
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
    locator_domain = "https://www.paultaiwan.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
