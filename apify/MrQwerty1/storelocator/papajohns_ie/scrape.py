from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state or ""
    postal = adr.postcode or SgRecord.MISSING

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://papajohns.ie/wp-admin/admin-ajax.php"
    data = {"action": "get_markers", "address": "", "distance": "50"}

    r = session.post(api, headers=headers, data=data)
    js = r.json()["markers"]

    for j in js:
        location_name = (
            j.get("location").replace("&#8217;", "'").replace("&#8211;", "-")
        )
        page_url = j.get("store_link")
        source = j.get("store_address") or "<html></html>"
        tree = html.fromstring(source)
        line = tree.xpath("//text()")
        raw_address = " ".join(list(filter(None, [l.strip() for l in line])))
        street_address, city, state, postal = get_international(raw_address)
        if len(state) == 3:
            postal = f"{state} {postal}"
            state = SgRecord.MISSING
        if postal == SgRecord.MISSING:
            postal = " ".join(raw_address.split(",")[-1].split()[-2:])

        if len(postal) > 8 or (len(postal) == 8 and " " not in postal):
            postal = SgRecord.MISSING

        phone = j.get("store_telephone")
        latitude = j.get("store_latitude")
        longitude = j.get("store_longitude")

        _tmp = []
        text = j.get("store_opening_hours") or "<html></html>"
        tree = html.fromstring(text)
        for i in range(1, 8):
            try:
                day = tree.xpath(f".//tr[1]/th[{i}]/text()")[0].strip()
                start = tree.xpath(f".//tr[2]/td[{i}]/text()")[0].strip()
                end = tree.xpath(f".//tr[4]/td[{i}]/text()")[0].strip()
                if not day:
                    continue
                _tmp.append(f"{day}: {start}-{end}")
            except IndexError:
                pass

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="IE",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://papajohns.ie/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
