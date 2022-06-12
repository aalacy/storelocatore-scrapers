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
    urls = []
    r = session.get("https://www.waitrose.com/content/waitrose/en/bf_home/bf.html")
    tree = html.fromstring(r.text)
    ids = tree.xpath("//select[@id='global-form-select-branch']/option/@value")
    for _id in ids:
        if not _id:
            continue
        urls.append(
            f"https://www.waitrose.com/content/waitrose/en/bf_home/bf/{_id}.html"
        )

    return urls


def get_js(lat, lng, _id):
    r = session.get(
        f"https://www.waitrose.com/shop/NearestBranchesCmd?latitude={lat}&longitude={lng}"
    )
    try:
        js = r.json()["branchList"]
    except:
        js = []
    out = dict()
    for j in js:
        if str(j.get("branchId")) == _id:
            out = j
            break

    return out


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    if r.status_code == 404:
        return
    tree = html.fromstring(r.text)

    latitude = "".join(tree.xpath("//a[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//a[@data-long]/@data-long"))
    store_number = page_url.split("/")[-1].replace(".html", "")

    j = get_js(latitude, longitude, store_number)
    if j:
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".strip()
        )
        city = j.get("city") or ""
        state = j.get("state")
        postal = j.get("postCode")
        phone = j.get("phoneNumber")
        location_type = j.get("branchDesc")
    else:
        location_name = "".join(
            tree.xpath("//h1[contains(text(), 'Welcome to')]/text()")
        )
        if "little" in location_name.lower():
            location_type = "Little Waitrose"
        else:
            location_type = "Standard Branch"
        line = tree.xpath("//div[@class='col branch-details']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            return
        if line[-2] == "U.A.E." or line[-2] == "677":
            return

        phone = line.pop()
        raw_address = ", ".join(line)
        street_address, city, state, postal = get_international(raw_address)

    _tmp = []
    tr = tree.xpath("//div[@class='tab' and not(@id)]//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[last()]//text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp)

    street_address = street_address.replace("&#039;", "'")
    city = city.replace("&#039;", "'")

    if "Little" in location_type:
        location_name = "Little Waitrose"
    elif "from" in location_type:
        location_name = location_type
    else:
        location_name = "Waitrose"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.waitrose.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
