from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_ids():
    ids = set()
    coords = dict()
    r = session.get(
        "https://www.cohenschemist.co.uk/wp-admin/admin-ajax.php?action=mycohens_ajax&task=GetMapXML&MappingFilter=ALL_BRANCHES"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker_generic")
    for marker in markers:
        _id = "".join(marker.xpath("./@id"))
        lat = "".join(marker.xpath("./@latitude"))
        lng = "".join(marker.xpath("./@longitude"))
        coords[_id] = (lat, lng)
        ids.add(_id)

    return ids, coords


def get_data(store_number, sgw: SgWriter, coords):
    page_url = "https://www.cohenschemist.co.uk/mycohens/directory/"

    data = {"task": "popup_BranchDetails", "BranchID": store_number}

    r = session.post(
        "https://www.cohenschemist.co.uk/wp-admin/admin-ajax.php?action=mycohens_ajax",
        data=data,
    )
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//strong/text()")[0].strip()
    line = tree.xpath("./text()")
    line = list(filter(None, [l.strip() for l in line]))
    phone = line[1].replace("|", "").strip() or SgRecord.MISSING
    line = line[0].upper()
    full_adr = line
    postal = line.split(",")[-1].strip()
    line = ",".join(line.split(",")[:-1]).strip()

    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or SgRecord.MISSING
    )

    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()

    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    country_code = "GB"
    latitude, longitude = coords.get(store_number)

    _tmp = []
    tr = tree.xpath("//tr[./td]")

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        start = "".join(t.xpath("./td[2]/text()")).strip()
        close = "".join(t.xpath("./td[3]/text()")).strip()
        if start == close:
            _tmp.append(f"{day}: Closed")
        else:
            if close != "Closed":
                _tmp.append(f"{day}: {start} & {close}")
            else:
                _tmp.append(f"{day}: {start}")
    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=full_adr,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids, coords = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, _id, sgw, coords): _id for _id in ids
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.cohenschemist.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
