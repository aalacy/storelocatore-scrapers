import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_states():
    req = session.get("https://www.kay.com/store-finder/view-all-states")
    root = html.fromstring(req.text)

    return root.xpath(
        "//h1[contains(text(), 'All Stores')]/following-sibling::div//a/@href"
    )


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    _tmp = []
    lat = "".join(tree.xpath(".//span[@itemprop='latitude']/text()")).strip()
    lng = "".join(tree.xpath(".//span[@itemprop='longitude']/text()")).strip()
    try:
        text = "".join(
            tree.xpath("//script[contains(text(), 'var storeInformation')]/text()")
        )
        text = (
            text.split('"openings":')[1]
            .split("},")[0]
            .replace("\n", "")
            .replace("\t", "")
            + "}"
        )
        j = json5.loads(text)
    except:
        j = dict()

    for k, v in j.items():
        _tmp.append(f"{k} {v}")

    return lat, lng, ";".join(_tmp)


def get_data(state, sgw: SgWriter):
    req = session.get(f"https://www.kay.com/store-finder/{state}")
    root = html.fromstring(req.text)

    divs = root.xpath("//div[@class='col-md-3 col-lg-3 col-sm-4 col-xs-12' and ./span]")
    for d in divs:
        slug = "".join(d.xpath(".//div[@class='viewstoreslist']/a/@href"))
        page_url = f"https://www.kay.com{slug}"
        if page_url.endswith("/null"):
            page_url = SgRecord.MISSING

        location_name = "".join(
            d.xpath(".//div[@class='viewstoreslist']/a/text()")
        ).strip()
        street_address = "".join(
            d.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        phone = "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()
        if page_url != SgRecord.MISSING:
            latitude, longitude, hours_of_operation = get_additional(page_url)
            store_number = page_url.split("-")[-1]
        else:
            latitude, longitude, hours_of_operation = (
                SgRecord.MISSING,
                SgRecord.MISSING,
                SgRecord.MISSING,
            )
            store_number = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    states = get_states()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, state, sgw): state for state in states
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.kay.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
