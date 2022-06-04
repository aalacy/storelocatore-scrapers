import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    postal = re.findall(r"\d{4}", line).pop()
    adr = parse_address(International_Parser(), line, postcode=postal)
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
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_urls():
    urls = []
    r = session.get("https://www.decathlon.ph/stores")
    links = set(re.findall(r'"slug":"(.+?)"', r.text))
    for link in links:
        isupper = bool(re.findall(r"\w*[A-Z]\w*", link))
        if isupper or "click-" in link or "footer" in link:
            continue
        urls.append(f"https://www.decathlon.ph/stores/{link}")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//div[@class='col-6 str-address']//h2[contains(text(), 'Decathlon')]/text()"
        )
    ).strip()
    raw_address = " ".join(
        tree.xpath(
            "//div[@class='col-6 str-address']//h2[not(contains(text(), 'Decathlon'))]/text()"
        )
    ).strip()
    street_address, city, state, postal = get_international(raw_address)
    if postal in street_address:
        street_address = raw_address.split(postal)[0].strip()[:-1]
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    lines = tree.xpath("//div//h2/text()")
    phone = lines[0]
    if "," in phone:
        phone = phone.split(",")[0].strip()
    hours_of_operation = ";".join(
        tree.xpath("//div[@class='row']/div[@class='col-6'][last()]//h2/text()")
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="PH",
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
    locator_domain = "https://www.decathlon.ph/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
