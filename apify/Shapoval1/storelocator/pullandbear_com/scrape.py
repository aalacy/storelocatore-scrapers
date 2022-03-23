from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

days = [
    "",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pullandbear.com/"
    api_url = "https://www.pullandbear.com/itxrest/2/catalog/store?brandId=2&appId=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:
        country_code = j.get("countryCode")
        country_id = j.get("id")
        r = session.get(
            f"https://www.pullandbear.com/itxrest/2/bam/store/{country_id}/physical-stores-by-country?countryCode={country_code}&appId=1",
            headers=headers,
        )

        try:
            js = r.json()["stores"]
        except:
            continue
        for j in js:

            page_url = "https://www.pullandbear.com/be/en/store-locator.html"
            location_name = j.get("name") or "<MISSING>"
            location_type = j.get("nameStoreType") or "<MISSING>"
            try:
                street_address = j.get("addressLines")[0]
            except:
                street_address = "<MISSING>"
            street_address = (
                str(street_address)
                .replace(", NEAR SYRIA & LEBANON BANK,", "")
                .replace(", TULIPANES", "")
                .strip()
            )
            state = j.get("state") or "<MISSING>"
            postal = j.get("zipCode") or "<MISSING>"
            if postal == "0":
                postal = "<MISSING>"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("id")
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            try:
                phone = j.get("phones")[0]
            except:
                phone = "<MISSING>"
            if phone == "-":
                phone = "<MISSING>"
            hours = []
            for hr in j.get("openingHours", {}).get("schedule", []):
                times = f"{hr['timeStripList'][0]['initHour']} - {hr['timeStripList'][0]['endHour']}"
                if len(hr["weekdays"]) == 1:
                    hh = hr["weekdays"][0]
                    hours.append(f"{days[hh]}: {times}")
                else:
                    day = f'{days[hr["weekdays"][0]]} to {days[hr["weekdays"][-1]]}'
                    hours.append(f"{day}: {times}")
            hours_of_operation = "; ".join(hours) or "<MISSING>"

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city}, {state} {postal}".replace(
                    "<MISSING>", ""
                ).strip(),
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
