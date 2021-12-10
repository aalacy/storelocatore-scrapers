from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jamaicablue.com.au"
    api_url = "https://jamaicablue.com.au/wp-json/store-locator/v1/store/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("web") or "<MISSING>"
        location_name = j.get("locname") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        ad = f"{j.get('address2')}".strip()
        state = ad.split()[-2].strip() or "<MISSING>"
        postal = ad.split()[-1].strip() or "<MISSING>"
        country_code = "AU"
        city = " ".join(ad.split()[:-2]) or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        tmp = []
        for d in days:
            day = d
            time = j.get("openHours").get(f"{d}")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = (
            "; ".join(tmp).replace("None", "Closed").strip() or "<MISSING>"
        )

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
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
