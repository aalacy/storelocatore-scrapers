from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def fetch_data(sgw: SgWriter):
    api_url = "https://corporate.dow.com/content/corp/en-us.corplocations.json"
    page_url = "https://corporate.dow.com/en-us/locations.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        source = j.get("address") or "<html></html>"
        tree = html.fromstring(source)
        lines = tree.xpath("//p//text()")
        _tmp = []
        for line in lines:
            if not line.strip() or "Dow in" in line:
                continue
            _tmp.append(line.strip())

        line = ", ".join(_tmp)
        adr = parse_address(International_Parser(), line)
        street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()

        city = adr.city
        if city == "City":
            lines = line.split(",")
            for li in lines:
                if "City" in li:
                    city = li.strip()
                    break
        if city == "Zip":
            city = line.split("(")[0].split(",")[-1].strip()
        state = adr.state
        postal = adr.postcode
        location_name = j.get("locationName")
        if not location_name:
            continue

        phone = j.get("telephone") or SgRecord.MISSING
        latitude = j.get("latitude") or SgRecord.MISSING
        longitude = j.get("longitude") or SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=SgRecord.MISSING,
            raw_address=line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://corporate.dow.com/"
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
