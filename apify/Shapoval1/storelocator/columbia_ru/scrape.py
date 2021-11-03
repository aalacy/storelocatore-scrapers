from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://columbia.ru"
    api_url = "https://columbia.ru/api/geo/shops"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["countries"]
    for j in js:
        country_code = j.get("name")
        page_url = "https://columbia.ru/stores"
        cities = j.get("cities")
        for c in cities:
            city = "".join(c.get("name")) or "<MISSING>"
            shops = c.get("shops")
            for s in shops:
                location_name = s.get("name") or "<MISSING>"
                street_address = "".join(s.get("address")) or "<MISSING>"
                if city in street_address:
                    try:
                        street_address = " ".join(
                            street_address.split(f"{city},")[1:]
                        ).strip()
                    except:
                        street_address = street_address
                store_number = s.get("shopNumber") or "<MISSING>"
                latitude = s.get("geoPoint").get("lat") or "<MISSING>"
                longitude = s.get("geoPoint").get("lon") or "<MISSING>"
                phone = s.get("phone") or "<MISSING>"
                hours_of_operation = " ".join(s.get("workTime")) or "<MISSING>"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
