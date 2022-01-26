from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://uk.virginmoney.com/"
    api_url = "https://api.woosmap.com/stores/search?key=woos-89a9a4a8-799f-3cbf-9917-4e7b88e46c30&lat=56.817642&lng=-5.111418&max_distance=500000&stores_by_page=300&limit=5000"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://uk.virginmoney.com",
        "Connection": "keep-alive",
        "Referer": "https://uk.virginmoney.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["features"]
    for j in js:
        try:
            a = j.get("properties")
        except:
            continue

        location_name = a.get("name") or "<MISSING>"
        adr = a.get("address").get("lines")
        street_address = ""
        location_type = ""
        tmp_street = []
        tmp_type = []
        for i in adr:
            if "Store closes" not in i:
                tmp_street.append(i)
            if "Store closes" in i:
                tmp_type.append(i)
            street_address = " ".join(tmp_street)
            location_type = " ".join(tmp_type)
        postal = "".join(a.get("address").get("zipcode"))
        country_code = "GB"
        city = "".join(a.get("address").get("city"))
        store_number = a.get("store_id")
        page_url = "https://uk.virginmoney.com/store-finder/"
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]
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
        for d in range(1, len(days) + 1):
            day = days[d - 1]
            try:
                opens = a.get("weekly_opening")[str(d)].get("hours")[0].get("start")
            except:
                opens = "Closed"

            try:
                closes = a.get("weekly_opening")[str(d)].get("hours")[0].get("end")
            except:
                closes = "Closed"
            line = f"{day} {opens} - {closes}"
            if opens == closes:
                line = f"{day} Closed"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=location_type,
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
