from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    base_link = base_link = "https://checkintocash.com/wp-admin/admin-ajax.php"

    coords = []
    found = []

    for num in range(1, 10):
        api_link = (
            "https://api.momentfeed.com/v1/analytics/api/llp/nearby.json?auth_token=HJIVDHNMZCCFWYZC&geo=39.07868,-108.58091&multi_account=false&page=%s&pageSize=100&radius=5000"
            % (num)
        )
        results = session.get(api_link, headers=headers).json()
        if len(results) == 0:
            break
        for r in results:
            coords.append(
                str(r["address_detail"]["latitude"])
                + ","
                + str(r["address_detail"]["longitude"])
            )

    for lat_lng in coords:
        if lat_lng in found:
            continue
        query_params = {"action": "store_locator", "latlng": lat_lng}
        api_data = session.post(base_link, headers=headers, data=query_params).json()
        stores = api_data["stores"]
        geos = api_data["markers"]

        for i, store in enumerate(stores):
            locator_domain = "checkintocash.com"

            geo = geos[i]
            link = store["url"]
            if link == geo["url"]:
                latitude = geo["position"]["lat"]
                longitude = geo["position"]["lng"]
                found.append(str(latitude) + "," + str(longitude))
            else:
                # This should never happen
                raise

            location_name = "Check Into Cash " + geo["cityState"]
            street_address = store["addressLine1"]
            city = store["city"]
            state = store["state"]
            zip_code = geo["postalCode"]
            country_code = "US"
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = store["phone"]

            hours_of_operation = ""
            raw_hours = store["openIntervals"]
            for hours in raw_hours:
                day = hours["dayOfWeek"]
                if len(day[0]) != 1:
                    day = " ".join(hours["dayOfWeek"])
                opens = hours["storeOpening"]
                closes = hours["storeClosing"]
                if opens != "" and closes != "":
                    clean_hours = day + " " + opens + "-" + closes
                    hours_of_operation = (
                        hours_of_operation + " " + clean_hours
                    ).strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
