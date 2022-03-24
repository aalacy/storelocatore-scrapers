from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dfs.co.uk/"
    api_url = "https://www.dfs.co.uk/wcs/resources/store/10202/stores?langId=-1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:

        a = j.get("address")
        slug = j.get("seoToken")
        page_url = f"https://www.dfs.co.uk/store-directory/{slug}"
        location_name = j.get("storeName") or "<MISSING>"
        street_address = (
            f"{a.get('line1')} {a.get('line2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("storeNumber") or "<MISSING>"
        try:
            latitude = j.get("yextRoutableCoordinate").get("latitude")
            longitude = j.get("yextRoutableCoordinate").get("longitude")
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("mainPhone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        hours = j.get("hours")
        tmp = []
        if hours:
            for d in days:
                day = d
                opens = hours.get(f"{d}").get("openIntervals")[0].get("start")
                closes = hours.get(f"{d}").get("openIntervals")[0].get("end")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
