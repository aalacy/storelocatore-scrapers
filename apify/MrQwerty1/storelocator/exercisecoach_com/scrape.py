from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://exercisecoach.com/find-a-studio/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='StudioName']/a/@href")


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


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//h2[@class='vc_custom_heading avenirbold']/a[not(contains(@href, 'map'))]/text()|//h2[@class='vc_custom_heading avenirbold']/text()"
        )
    ).strip()
    line = tree.xpath(
        "//p[@style='font-size: 21px; line-height: 33px; color: #3d454b;']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].replace(".", "")
    try:
        postal = line.split()[1]
    except IndexError:
        postal = SgRecord.MISSING
    phone = "".join(tree.xpath("//p/a[contains(@href, 'tel:')]/text()")).strip()

    text = "".join(
        tree.xpath(
            "//h2[@class='vc_custom_heading avenirbold']/a[contains(@href, 'map')]/@href"
        )
    )
    latitude, longitude = get_coords_from_google_url(text)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://exercisecoach.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
