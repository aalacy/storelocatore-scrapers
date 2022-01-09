from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(coord, sgw: SgWriter):
    lat, lng = coord
    api = f"https://dealerlocator.fiat.com/geocall/RestServlet?mkt=3112&brand=00&func=finddealerxml&serv=sales&track=1&x={lng}&y={lat}&rad=100"
    r = session.get(api, headers=headers)

    tree = html.fromstring(r.content)
    divs = tree.xpath("//dealer")

    for d in divs:
        location_name = "".join(d.xpath("./companynam/text()")).strip()
        if not location_name:
            continue
        page_url = "".join(d.xpath("./website/text()")).strip()
        street_address = "".join(d.xpath("./address/text()")).strip()
        city = "".join(d.xpath("./town/text()")).strip()
        state = "".join(d.xpath("./province/text()")).strip()
        postal = "".join(d.xpath("./zipcode/text()")).replace("_", " ").strip() or "1"
        if postal[0].isdigit():
            continue
        phone = "".join(d.xpath("./tel_1/text()")).strip()
        latitude = "".join(d.xpath("./ycoord/text()")).strip()
        longitude = "".join(d.xpath("./xcoord/text()")).strip()
        store_number = "".join(d.xpath("./maincode/text()")).strip()

        _tmp = []
        li = d.xpath("./activity/*")
        for l in li:
            day = "".join(l.xpath("./dateweek/text()")).strip()
            start = "".join(l.xpath("./morning_from/text()")).strip()
            end = "".join(l.xpath("./afternoon_to/text()")).strip()
            if not start:
                continue
            start = start[:2] + ":" + start[2:]
            end = end[:2] + ":" + end[2:]
            _tmp.append(f"{day}: {start} - {end}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.fiat.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for coords in DynamicGeoSearch(
            country_codes=[SearchableCountries.BRITAIN], max_search_distance_miles=100
        ):
            fetch_data(coords, writer)
