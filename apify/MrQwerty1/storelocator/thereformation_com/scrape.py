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


def get_urls():
    r = session.get("https://www.thereformation.com/stores.html")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(@href, '/stores/')]/@href"))


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@class='col-12 col-lg-6 store-page__details']//text()")
    line = list(filter(None, [" ".join(l.split()).strip() for l in line]))
    if "coming soon" in line[0].lower():
        return

    text = "".join(tree.xpath("//span[@class='store-details']/a/@href"))
    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]

    cnt = 0
    for li in line:
        if "Hours:" in li:
            break
        cnt += 1

    adr = line[line.index("Address:") + 1 : cnt]
    raw_address = ", ".join(adr).replace(",,", ",")
    street_address, city, state, postal = get_international(raw_address)
    if "East" in street_address:
        street_address = street_address.replace("East", "").strip()
        city = f"East {city}"
    if not city:
        city = raw_address.split(",")[-1].strip()

    if "london" in raw_address.lower():
        country = "GB"
    elif "toronto" in raw_address.lower():
        country = "CA"
    else:
        country = "US"

    phone = line[line.index("Call:") + 1]
    hours = line[cnt + 1 : line.index("Call:")] or line[cnt : line.index("Call:")]
    hours_of_operation = ";".join(hours).replace("Hours:", "").strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country,
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
    locator_domain = "https://www.thereformation.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
