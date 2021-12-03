from sgscrape.sgpostal import USA_Best_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }

    r = session.get("https://www.urgentteam.com/location-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.urgentteam.com"
    page_url = url
    if page_url == "https://www.urgentteam.com/locations/":
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath('//h1[@class="o-location-hero__title u-h2"]/text()')
    )
    ad = " ".join(
        tree.xpath("//h3[contains(text(), 'Address')]/following-sibling::a[1]/text()")
    ).strip()
    if ad.count("Cullman") == 2 or ad.count("Huntsville") == 2:
        ad = " ".join(
            tree.xpath(
                "//h3[contains(text(), 'Address')]/following-sibling::a/text()[1]"
            )
        ).strip()

    a = parse_address(USA_Best_Parser(), ad)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    try:
        state = location_name.split("in ")[1].split(",")[1].strip()
    except:
        state = "<MISSING>"
    if state.find("(") != -1:
        state = state.split("(")[0].strip()
    postal = a.postcode or "<MISSING>"
    country_code = "US"
    city = location_name.split("in")[1].split(",")[0].strip()

    phone = (
        "".join(tree.xpath("//p[contains(text(), 'Phone')]/a/text()")) or "<MISSING>"
    )
    ll = (
        "".join(
            tree.xpath('//img[@class="lazyload m-location-panel__static-map"]/@src')
        )
        .split("center=")[1]
        .split("&")[0]
    )
    latitude = ll.split(",")[0]
    longitude = ll.split(",")[1]
    location_type = "".join(
        tree.xpath("//h3[@class='m-location-panel__subheading']/text()")
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="m-location-panel__hours m-location-hours"]//text()'
            )
        )
        .replace("\n", "")
        .replace("   ", " ")
        .strip()
        or "<MISSING>"
    )
    coming_soon = (
        "".join(
            tree.xpath(
                '//article[@class="o-location-hero__panel m-location-panel m-location-panel--coming-soon"]/div/@data-bg'
            )
        )
        or "<MISSING>"
    )
    if coming_soon.find("COMING-SOON") != -1:
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):

    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
