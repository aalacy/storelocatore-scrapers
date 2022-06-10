import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def fetch_data(sgw: SgWriter):
    api = "http://www.gulf.pl/wp-admin/admin-ajax.php?action=loadDistributors"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        g = j.get("geolocation") or {}
        raw_address = g.get("address") or ""
        postal = "".join(re.findall(r"\d{2,3}.\d{3}", raw_address))
        if not postal:
            street_address, city = raw_address.split(", ")
        else:
            adr = raw_address.replace(", Polska", "").split(postal)
            adr = list(filter(None, [a.strip() for a in adr]))
            if len(adr) == 2:
                street_address, city = adr
            else:
                line = adr.pop()
                if "Warszawa" in line:
                    street_address = line.replace("Warszawa", "").strip()
                    city = "Warszawa"
                else:
                    street_address, city = get_international(line)

        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = j.get("region")
        country_code = "PL"
        location_type = ", ".join(j.get("services") or [])
        location_name = j.get("title")
        phone = j.get("phone") or ""
        phone = phone.replace("tel.", "").strip()
        latitude = g.get("lat")
        longitude = g.get("lng")

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
            location_type=location_type,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.gulf.pl/"
    page_url = "http://www.gulf.pl/punkty-sprzedazy-gulf/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
