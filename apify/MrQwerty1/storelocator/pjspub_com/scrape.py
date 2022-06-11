from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    r = session.get("https://pjspub.com/choose.php", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@id='container']/div/p/a[not(contains(@href, '#'))]/@href")


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_arena_venues(sgw: SgWriter):
    page_url = "https://pjspub.com/about.php?loc=Arena_Venues"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//p[@class='locationinfo']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[contains(@style, 'color:#000;')]/text()")
        ).strip()
        line = d.xpath(".//a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        line.pop()
        if not line:
            continue

        street_address = ", ".join(line[:-1]).strip()
        line = line[-1]
        city = line.split(",")[0].strip()
        state = line.split(",")[1].strip()
        text = "".join(d.xpath(".//a/@href"))
        latitude, longitude = get_coords_from_google_url(text)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def get_data(slug, sgw: SgWriter):
    page_url = f"{locator_domain}{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h3[@class='locationinfo-location']/text()")
    ).strip()
    line = tree.xpath(
        "//div[@id='locationinfo-address']/p[@class='locationinfo']/a/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    phone = (
        "".join(
            tree.xpath(
                "//div[@id='locationinfo-address']/p[@class='locationinfo']/text()"
            )
        )
        .replace("p.", "")
        .strip()
    )

    text = "".join(
        tree.xpath("//div[@id='locationinfo-address']/p[@class='locationinfo']/a/@href")
    )
    latitude, longitude = get_coords_from_google_url(text)

    _tmp = []
    hours = tree.xpath(
        "//div[@id='locationinfo-hours']/p[@class='locationinfo']//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))

    for h in hours:
        if "dine" in h.lower() or (h.startswith("(") and h.endswith(")")):
            continue
        if "kitchen" in h.lower():
            continue
        if "(" in h:
            h = h.split("(")[0].strip() + " " + h.split(")")[1].strip()

        _tmp.append(h)

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    get_arena_venues(sgw)
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://pjspub.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
