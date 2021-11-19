from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.mattisonsalonsuites.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@id,'button-id-') and contains(@href, '/location/')]/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1[@class='page-header-title inherit']/text()")
    ).strip()
    street_address = (
        "".join(tree.xpath("//*[@class='company-info-address']/span/span[1]/text()"))
        .replace("\n", ", ")
        .strip()
    )
    if "We " in street_address:
        street_address = street_address.split("We ")[0].strip()
    if "Summerfield Crossing North" in street_address:
        street_address = street_address.replace(
            "Summerfield Crossing North", ""
        ).strip()
    city = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[2]/text()")
    ).strip()
    state = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[3]/text()")
    ).strip()
    postal = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[4]/text()")
    ).strip()
    phone = "".join(
        tree.xpath("//*[@class='company-info-phone']/span/a/text()")
    ).strip()
    if not phone:
        phone = "".join(
            tree.xpath(
                "//a[@id='button-id-1']//span[@class='button-sub-text body-font']/text()"
            )
        ).strip()

    _tmp = []
    days = tree.xpath(
        "//div[@class='locations-single-address']//span[@class='company-info-hours-day']/text()"
    )
    times = tree.xpath(
        "//div[@class='locations-single-address']//li[@class='company-info-hours-openclose']/text()"
    )

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "https://www.mattisonsalonsuites.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
