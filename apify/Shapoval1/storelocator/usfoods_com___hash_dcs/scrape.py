from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.usfoods.com/"
    api_url = "https://www.usfoods.com/bin/usfoods/location-query?nocache=true&data=%7B%22locationFallback%22%3A%22locationNoFilters%22%2C%22locationTypes%22%3A%5B%5D%2C%22shoppingTypes%22%3A%5B%5D%2C%22excludeTags%22%3A%5B%22us-foods%3Afuture%22%5D%7D"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["message"]
    for j in js:

        page_url = j.get("pagePath")
        if str(page_url).find("usfoods") == -1:
            page_url = "https://www.usfoods.com/locations.html"
        location_name = j.get("displayTitle") or "<MISSING>"
        loc_type = j.get("locationTypes")
        sub_type = "".join(j.get("type")).replace("-", " ").strip()
        tmp = []
        for l in loc_type:
            l = str(l).split("/")[-1].replace("-", " ").strip()
            tmp.append(l)
        location_type = ", ".join(tmp) or sub_type
        street_address = j.get("street") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
