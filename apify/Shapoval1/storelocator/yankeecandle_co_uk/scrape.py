from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.yankeecandle.co.uk/"
    types_value = [1, 3, 6]
    for type in types_value:
        api_url = f"https://storescontent.yankeecandle.co.uk/searchQuery?lat=51.5122712&long=-0.1149584&radius=100000&storeType={type}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()["stores"]
        for j in js:

            page_url = "https://www.yankeecandle.co.uk/stores"
            location_name = j.get("label") or "<MISSING>"
            street_address = f"{j.get('address')} {j.get('address2')}".replace(
                "None", ""
            ).strip()
            state = j.get("state").get("abbr") or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("long") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            store_number = j.get("id")
            location_type = "<MISSING>"
            if type == 1:
                location_type = "Yankee Candle® Stockists"
            if type == 3:
                location_type = "Outlet Stores"
            if type == 6:
                location_type = "WoodWick® Stockists"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=SgRecord.MISSING,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
