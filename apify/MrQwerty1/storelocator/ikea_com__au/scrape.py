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
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.ikea.com/au/en/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(@href, 'au/en/stores/')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    phone = "".join(
        tree.xpath(
            "//h2[./strong[contains(text(), 'Address')]]/following-sibling::p[2]/text()"
        )
    )
    location_name = "".join(
        tree.xpath("//h1[contains(@class, 'pub__h1')]/text()")
    ).strip()
    lines = tree.xpath(
        "//h2[./strong[contains(text(), 'Address')]]/following-sibling::p[1]/text()"
    )
    lines = list(filter(None, [line.strip() for line in lines]))
    if "T:" in lines[-1]:
        phone = lines.pop()
    phone = phone.replace("T:", "").strip()
    if len(phone) > 15:
        phone = SgRecord.MISSING

    raw_address = ", ".join(lines).strip()
    if "(" in raw_address:
        raw_address = (
            raw_address[: raw_address.index("(")]
            + raw_address[raw_address.index(")") + 1 :]
        )
    raw_address = raw_address.replace(",,", ",").replace(", ,", ",")
    street_address, city, state, postal = get_international(raw_address)

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//h4[./strong[contains(text(), 'Store')]]/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="AU",
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
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
    locator_domain = "https://www.ikea.com/au"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
