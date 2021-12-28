from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.obag.us.com/us/storelocator/index/storesbycurrentzoom?ajax=1&lat1=-90&lng1=-180&lat2=90&lng2=180&loadedMarkers="
    headers = {"X-Requested-With": "XMLHttpRequest"}

    r = session.get(api_url, headers=headers)
    js = r.json()["items"]

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = j.get("shop_view_url")
        location_name = j.get("title")
        phone = j.get("phone_1") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = j.get("working_times") or []
        d = {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],
            "6": [],
            "7": [],
        }  # type: dict

        for h in hours:
            index = h.get("day")
            start = h.get("from")
            end = h.get("to")
            period = f"{start} - {end}"
            d[str(index)].append(period)

        for day, period in zip(days, d.values()):
            _tmp.append(
                f'{day}: {" ".join(period)}'.replace(
                    "00:00 - 00:00 00:00 - 00:00", "Closed"
                ).replace("00:00 00:00 -", "")
            )

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.obag.us.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
