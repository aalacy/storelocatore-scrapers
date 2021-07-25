from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = (
        "https://www.miumiu.com/us/en/store-locator.miumiu.getAllStoresByBrand.json"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["allStores"]
    for j in js.values():
        country_code = j.get("country")
        if country_code != "US":
            continue
        slug = "".join(j.get("storeName"))
        page_url = f"https://www.miumiu.com/us/en/store-detail.{slug}.html"
        try:
            location_name = j.get("Description")[0].get("displayStoreName")
        except:
            location_name = j.get("Description").get("displayStoreName")
        street_address = "".join(j.get("addressLine")[0]).replace(
            "9700 Collins Avenue,", "9700 Collins Avenue"
        )
        street_address = street_address.split(",")[0].replace("NY", "")
        phone = j.get("telephone1")
        state = j.get("stateOrProvinceName")
        postal = j.get("postalCode")
        city = j.get("city")
        days = [
            "sunday",
            "saturday",
            "tuesday",
            "friday",
            "wednesday",
            "thursday",
            "monday",
        ]
        tmp = []
        for d in days:
            days = "".join(d)
            times = j.get("Attribute").get("WH_DAY").get(f"{d}")
            line = f"{days} {times}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp)
        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.miumiu.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
