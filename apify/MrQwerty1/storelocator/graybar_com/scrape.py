from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000):
        r = session.get(
            f"https://www.graybar.com/store-finder?q=&page={i}&latitude=38.6994076&longitude=-90.4384332",
            headers=headers,
        )

        try:
            js = r.json()["data"]
        except:
            break

        for j in js:
            location_name = j.get("displayName")
            street_address = f"{j.get('line1')} {j.get('line2') or ''}".strip()
            city = j.get("town")
            state = j.get("region")
            postal = j.get("postalCode")
            country_code = "US"
            slug = j.get("url") or "?"
            slug = slug.split("?")[0]
            page_url = f"https://www.graybar.com{slug}"
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            hours = j.get("openingHours") or []
            for h in hours:
                location_type = h.get("type")
                times = h.get("times")
                _tmp = []
                for t in times:
                    day = t.get("weekDay")
                    opening = t.get("opening")
                    close = t.get("closing")
                    if opening:
                        _tmp.append(f"{day}: {opening} - {close}")
                    else:
                        _tmp.append(f"{day}: Closed")

                hours_of_operation = ";".join(_tmp)
                if hours_of_operation.count("Closed") == 7:
                    continue

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)

        if len(js) < 10:
            break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://graybar.com/"
    headers = {"Accept": "application/json"}
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
