from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def isalways(code):
    api = f"https://datastore-webapp-p.azurewebsites.net/REVERSE/api/Info/Poi?Lang=fr_FR&AdditionalData=Items&AdditionalDataFields=Items_Code,Items_Price,Items_Availability,Items_UpdateDate&Code={code}"
    r = session.get(api, headers=headers)
    j = r.json()["Pois"][0]
    message = j.get("RequMessage") or ""
    if "24" in message:
        return True
    return False


def fetch_data(sgw: SgWriter):
    for cnt in range(1, 5000):
        is24 = False
        store_number = "TEUK" + str(cnt).zfill(3)
        api = f"https://api.woosmap.com/stores/{store_number}"
        r = session.get(api, headers=headers, params=params)
        if r.status_code == 404:
            break

        js = r.json()
        j = js.get("properties")
        g = js.get("geometry")
        location_name = j.get("name")
        a = j.get("address") or {}
        lines = a.get("lines") or []
        street_address = " ".join(lines).strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = a.get("city")
        postal = a.get("zipcode") or ""
        postal = postal.replace(".", "")

        try:
            phone = j["contact"]["phone"]
        except:
            phone = SgRecord.MISSING
        longitude, latitude = g.get("coordinates") or [
            SgRecord.MISSING,
            SgRecord.MISSING,
        ]

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
        hours = j.get("weekly_opening") or {}
        hours.pop("timezone", None)
        for k, v in hours.items():
            day = days[int(k) - 1]
            try:
                start = v["hours"][0]["start"]
                end = v["hours"][0]["end"]
            except:
                continue
            _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        tags = j.get("tags") or []
        for t in tags:
            if "24" in t:
                is24 = True
                break

        if not is24 and not hours_of_operation:
            is24 = isalways(store_number)

        if is24:
            hours_of_operation = "Open 24hrs Monday - Sunday"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "totalenergies.uk"
    page_url = "https://services.totalenergies.uk/total-energies-service-stations"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Origin": "https://services.totalenergies.uk",
    }

    params = (("key", "mapstore-prod-woos"),)
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
