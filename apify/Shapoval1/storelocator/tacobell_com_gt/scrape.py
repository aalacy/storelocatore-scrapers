from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tacobell.com.gt/"
    api_url = "https://api.storepoint.co/v1/15ea25524ba2a9/locations?lat=14.6228&long=-90.5314&radius=100000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]["locations"]
    for j in js:

        page_url = "https://www.tacobell.com.gt/ubicaciones"
        location_name = j.get("name") or "<MISSING>"
        ad = "".join(j.get("streetaddress"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if postal == "ZONA 1":
            postal = "<MISSING>"
        country_code = "Guatemala"
        city = a.city or "<MISSING>"
        latitude = j.get("loc_lat") or "<MISSING>"
        longitude = j.get("loc_long") or "<MISSING>"
        hours_of_operation = f"Monday {j.get('monday')} Tuesday {j.get('tuesday')} Wednesday {j.get('wednesday')} Thursday {j.get('thursday')} Friday {j.get('friday')} Saturday {j.get('saturday')} Sunday {j.get('sunday')}"

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
