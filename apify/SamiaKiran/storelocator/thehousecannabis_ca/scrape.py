import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thehousecannabis_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://thehousecannabis.ca"
MISSING = SgRecord.MISSING

api_url = "https://mystudio.academy/Api/general/getcompanyDetailsForLandingPage"


def fetch_data():
    daylist = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    if True:
        url = "https://thehousecannabis.ca/stores/"
        r = session.get(url)
        log.info("Fetching the Token for the API....")
        token_url = DOMAIN + r.text.split('"app":["')[1].split('"')[0]
        r = session.get(token_url)
        token = r.text.split('Authorization:"')[2].split('"')[0]
        api_url = "https://plus.dutchie.com/plus/2021-07/graphql"
        payload = json.dumps(
            {
                "operationName": "Retailer",
                "variables": {},
                "query": "fragment hoursDayFragment on HoursDay {\n  active\n  start\n  end\n  __typename\n}\n\nfragment hoursFragment on Hours {\n  Sunday {\n    ...hoursDayFragment\n    __typename\n  }\n  Monday {\n    ...hoursDayFragment\n    __typename\n  }\n  Tuesday {\n    ...hoursDayFragment\n    __typename\n  }\n  Wednesday {\n    ...hoursDayFragment\n    __typename\n  }\n  Thursday {\n    ...hoursDayFragment\n    __typename\n  }\n  Friday {\n    ...hoursDayFragment\n    __typename\n  }\n  Saturday {\n    ...hoursDayFragment\n    __typename\n  }\n  __typename\n}\n\nquery Retailer {\n  retailers {\n    id\n    name\n    address\n    hours {\n      delivery {\n        ...hoursFragment\n        __typename\n      }\n      pickup {\n        ...hoursFragment\n        __typename\n      }\n      special {\n        startDate\n        endDate\n        hoursPerDay {\n          date\n          deliveryHours {\n            ...hoursDayFragment\n            __typename\n          }\n          pickupHours {\n            ...hoursDayFragment\n            __typename\n          }\n          __typename\n        }\n        name\n        __typename\n      }\n      __typename\n    }\n    coordinates {\n      latitude\n      longitude\n      __typename\n    }\n    __typename\n  }\n}\n",
            }
        )
        headers = {
            "authority": "plus.dutchie.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": token,
            "content-type": "application/json",
            "origin": "https://thehousecannabis.ca",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        }
        loclist = session.post(api_url, headers=headers, data=payload).json()["data"][
            "retailers"
        ]
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            phone = MISSING
            address = loc["address"].split(",")
            street_address = address[0]
            country_code = address[-1]
            city = address[1]
            address = address[2].split()
            state = address[0]
            zip_postal = address[-2] + " " + address[-1]
            latitude = loc["coordinates"]["latitude"]
            longitude = loc["coordinates"]["longitude"]
            hour_list = loc["hours"]["delivery"]
            hours_of_operation = ""
            for idx, hour in enumerate(hour_list):
                try:
                    day = daylist[idx]
                except:
                    continue
                time = hour_list[day]["start"] + "-" + hour_list[day]["end"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
