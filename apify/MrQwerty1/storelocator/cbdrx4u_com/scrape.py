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
    street = f"{adr.street_address_1} {adr.street_address_2}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode or ""

    return street, city, state, postal


def get_urls():
    urls = set()
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Virginia",
        "West Virginia",
        "Wisconsin",
        "United Kingdom",
    ]

    for state in states:
        slug = state.lower().replace(" ", "-")
        if "alabama" in slug:
            url = f"https://truecbd4u.com/find-us/{slug}/"
        else:
            url = f"https://cbdrx4u.com/find-us/{slug}"
        r = session.get(url)
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[text()='Show Details']/@href")
        for link in links:
            urls.add(link)

        if len(links) == 50:
            states.append(f"{slug}/2")

    return urls


def get_data(slug, sgw: SgWriter):
    if "alabama" in slug:
        page_url = f"https://truecbd4u.com{slug}"
    else:
        page_url = f"https://cbdrx4u.com{slug}"
    r = session.get(page_url)
    if r.status_code == 404:
        return
    tree = html.fromstring(r.text)

    location_name = " ".join(
        "".join(tree.xpath("//div[@class='text-xl font-bold']/text()")).split()
    )
    if "https" in location_name:
        location_name = location_name.split("https")[0].strip()
    line = tree.xpath("//div[@class='text-xl font-bold']/following-sibling::text()")
    line = list(filter(None, [" ".join(li.split()) for li in line]))
    raw_address = ", ".join(line)
    if "https" in raw_address:
        raw_address = raw_address.split("https")[0] + "," + raw_address.split(",")[-1]

    country_code = "US"
    street_address, city, state, postal = get_international(raw_address)
    if len(postal) > 5:
        country_code = "GB"
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "https://cbdrx4u.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
