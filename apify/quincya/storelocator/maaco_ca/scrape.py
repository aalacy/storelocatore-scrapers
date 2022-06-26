from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import sglog

log = sglog.SgLogSetup().get_logger("maaca.com")


def fetch_data(sgw: SgWriter):

    headers = {
        "apikey": "5678AKIAVAOWLJICABYD4CDQhjhjhfjdkm",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "content-type": "application/json",
    }

    session = SgRequests()

    locator_domain = "https://www.maaco.ca/"

    base_link = "https://dbrmcplipc.interplay.iterate.ai/api/v1/states"
    city_link = "https://dbrmcplipc.interplay.iterate.ai/api/v1/cities/"
    loc_link = "https://dbrmcplipc.interplay.iterate.ai/api/v1/location"

    json = {"country_code": "Canada"}
    states = session.post(base_link, headers=headers, json=json).json()["message"]

    for i in states:
        state_name = i["stateName"]
        state_code = i["stateAbbreviation"].lower()
        log.info(state_name)
        city_json = {"state": state_name}
        cities = session.post(city_link, headers=headers, json=city_json).json()[
            "cities"
        ]

        for city_name in cities:
            locs_json = {"city": city_name, "state": state_name, "country": "canada"}
            stores = session.post(loc_link, headers=headers, json=locs_json).json()[0][
                "stores"
            ]

            for store in stores:
                location_name = store["store_name"]
                street_address = store["store_address"]
                city = store["store_city"]
                state = store["store_state"]
                zip_code = store["store_postcode"]
                if zip_code.isdigit():
                    continue
                country_code = "CA"
                store_number = store["store_id"]

                link = (
                    "https://www.maaco.ca/locations/"
                    + state_code
                    + "/"
                    + city.replace(" ", "-").lower()
                    + "-"
                    + str(store_number)
                )

                phone = store["organic_phone"].replace("�", "").strip()
                if not phone:
                    log.info("Getting phone for: " + link)
                    api_link = (
                        "https://dbrmcplipc.interplay.iterate.ai/api/v1/store/"
                        + str(store_number)
                    )
                    store_det = session.get(api_link, headers=headers).json()
                    try:
                        phone = store_det["trackingPhone"].replace("�", "").strip()
                    except:
                        phone = ""
                location_type = ""
                latitude = store["store_lat"]
                longitude = store["store_long"]

                hours_of_operation = ""
                raw_hours = store["hours"]
                for day in raw_hours:
                    opens = raw_hours[day]["open"]
                    closes = raw_hours[day]["close"]
                    clean_hours = day + " " + opens + "-" + closes
                    hours_of_operation = (
                        (hours_of_operation + " " + clean_hours)
                        .strip()
                        .replace("Closed-Closed", "Closed")
                        .replace("CLOSED-CLOSED", "CLOSED")
                        .replace("By Appt.-By Appt.", "By Appt.")
                    )

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
