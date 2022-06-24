from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.consol.eu/"
    api_url = "https://www.consol.eu/Umbraco/Surface/StudioLocationSurface/GetAllStudioLocations?_=1642669952673"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        store_number = j.get("studioid")
        node = j.get("nodeId")
        latitude = j.get("lat")
        longitude = j.get("lng")
        if latitude == 0:
            latitude, longitude = "<MISSING>", "<MISSING>"
        r = session.get(
            f"https://www.consol.eu/Umbraco/Surface/StudioLocationSurface/GetStudioDetails?nodeId={node}"
        )
        js = r.json()
        slug = js.get("url")
        page_url = f"https://www.consol.eu{slug}"
        location_name = js.get("name")
        ad = js.get("address") or "<MISSING>"
        ad = str(ad).replace("\n", " ").strip()
        ad = " ".join(ad.split())
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if ad != "<MISSING>":
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address.isdigit():
                street_address = "".join(js.get("address")).split("\n")[0].strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "UK"
            city = a.city or "<MISSING>"
            if city == "<MISSING>":
                city = location_name
        if street_address.find(f"{postal}") != -1:
            street_address = (
                street_address.split(f"{postal}")[0]
                .replace(",", "")
                .replace(f" {city}", "")
                .strip()
            )

        hours_of_operation = (
            f"{js.get('openingTime')} - {js.get('closingTime')}".strip()
        )
        if "COMING SOON" in location_name:
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
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
