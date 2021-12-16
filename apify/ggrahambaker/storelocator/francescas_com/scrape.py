from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.francescas.com/api/commerce/storefront/locationUsageTypes/SP/locations/?startIndex=0&pageSize=453&filter=geo%20near(39.0718795%2C-94.9143239%2C10000000)&includeAttributeDefinition=true"
    session = SgRequests()

    cookies = {
        "sb-sf-at-prod": "at=9AQlj%2FOkUGeF9XjLQn9yvUmCG9bZXk2y5hrW1x6%2F1zrazXNN9Mb3dg5AtCEl4GTZ%2BhGxre7SCMpGrWKFsYSmxRulELnh8APVsg1gS6AlJRODziLZSgLmQiycmIByx8nlscHyvl8NZMpGbHrj95je2ctn8mwlDGqYex1GN1la4rttbfHnjIjWcUunOtxCgnIds8vK3b1hrN4PLL6qSt2lJi6BvBs7VLA0gRw6ujPtt7PCwE4MK6zsxkyHi%2BwjCtZYjfQaqmhnrR%2BKZePX2l%2BatujtwY%2F0Jhj5KaN4Xutb5tJBaqTqD2FMgVi5Exc7B8m4qxoylOErFEVq2yN9ISbymw%3D%3D",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers, cookies=cookies)

    js = r.json()
    for j in js["items"]:

        a = j.get("address")
        location_name = j.get("name")
        street_address = f"{a.get('address1')} {a.get('address2')}".strip()
        state = a.get("stateOrProvince") or "<MISSING>"
        postal = a.get("postalOrZipCode") or "<MISSING>"
        country_code = "US"
        city = a.get("cityOrTown") or "<MISSING>"
        store_number = j.get("code") or "<MISSING>"
        slug = "".join(location_name).split("#")[0].strip().lower().replace(" ", "-")
        page_url = f"https://www.francescas.com/store-details/{store_number}/{slug}"
        latitude = j.get("geo").get("lat") or "<MISSING>"
        longitude = j.get("geo").get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        tmp = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for d in days:
            day = d
            times = j.get("regularHours").get(f"{d}").get("label")
            line = f"{day} {times}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        if "".join(location_name).find("francescascollections") != -1:
            page_url = "https://www.francescas.com/store-details/francescascollections/"
            store_number = "<MISSING>"

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
    locator_domain = "https://www.francescas.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
