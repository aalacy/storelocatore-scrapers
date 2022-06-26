from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kochloeffel.de/"
    api_url = "https://uberall.com/api/storefinders/eBl6tjXNV9701BugQdZS474CISMcGE/locations/all?v=20211005&language=de&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&https://www.kochloeffel.de/restaurantfinder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["response"]["locations"]
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("streetAndNumber") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(
            f"https://uberall.com/api/storefinders/eBl6tjXNV9701BugQdZS474CISMcGE/locations/{store_number}"
        )
        js = r.json()["response"]
        phone = js.get("phone") or "<MISSING>"
        page_url = f"https://www.kochloeffel.de/restaurantfinder/l/{str(city).replace('(','-').replace(')','-').replace(' ','').lower().strip()}/{str(street_address).replace(' ','-').lower().strip()}/{store_number}".replace(
            "ß", "ss"
        ).strip()
        tmp = []
        hours = js.get("openingHours")
        hours_of_operation = "<MISSING>"
        if hours:
            for h in hours:
                day = (
                    str(h.get("dayOfWeek"))
                    .replace("1", "Monday")
                    .replace("2", "Tuesday")
                    .replace("3", "Wednesday")
                    .replace("4", "Thursday")
                    .replace("5", "Friday")
                    .replace("6", "Saturday")
                    .replace("7", "Sunday")
                )
                opens = h.get("from1")
                closes = h.get("to1")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp).replace("None - None", "Closed").strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
