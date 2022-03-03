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


def get_params():
    params = list()
    r = session.get("https://www.jollibeeuae.com/store-locator")
    tree = html.fromstring(r.text)
    divs = tree.xpath("//td[contains(@id, 'maid')]")
    for d in divs:
        _id = "".join(d.xpath("./@id")).replace("maid", "")
        location_name = "".join(d.xpath("./strong/text()")).strip()
        params.append({"id": _id, "name": location_name})

    return params


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(param, sgw: SgWriter):
    store_number = param.get("id")
    location_name = param.get("name")
    page_url = f"https://www.jollibeeuae.com/store-detail{store_number}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    raw_address = "".join(
        tree.xpath("//th[contains(text(), 'ADDRESS')]/following-sibling::td/text()")
    ).strip()
    street_address, city, state, postal = get_international(raw_address)

    text = "".join(tree.xpath(f"//iframe[@id='map{store_number}']/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath(
        "//table[@class='table table-hover table-striped']//tr[not(./th)]"
    )
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        inter = "".join(h.xpath("./td[last()]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="AE",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.jollibeeuae.com/"
    session = SgRequests(verify_ssl=False)

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
