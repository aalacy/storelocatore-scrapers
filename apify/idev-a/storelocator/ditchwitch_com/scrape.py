from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ditchwitch")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "http://ditchwitch.com/"
base_url = "https://www.ditchwitch.com/find-a-dealer"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

json_url = "https://hosted.where2getit.com/ditchwitch/rest/locatorsearch?like=0.22822414982857775&lang=en_US"

coords = [
    (40.75368539999999, -73.9991637),
    (3.216264063853835, 23.092478837961707),
    (8.873924062928575, -67.8303725109154),
    (-25.180938219545883, -62.55693492432918),
    (26.57294931161124, 5.997752650887076),
    (58.8956478624396, 47.8336901788746),
    (62.827134824567196, 116.03681483952685),
    (31.488776327650406, 104.43525246284652),
    (-19.161622877728977, 129.57197119797826),
]

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        for coord in coords:
            logger.info(coord)
            payload = {
                "request": {
                    "appkey": "FA8D823E-C7EC-11EC-973C-ED5D58203F82",
                    "formdata": {
                        "geoip": "false",
                        "dataview": "store_default",
                        "limit": 10000,
                        "atleast": 1,
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": "",
                                    "country": "",
                                    "latitude": coord[0],
                                    "longitude": coord[1],
                                    "state": "",
                                    "province": "",
                                    "city": "",
                                    "address1": "",
                                    "postalcode": "",
                                }
                            ]
                        },
                        "searchradius": "5000",
                        "radiusuom": "",
                        "where": {},
                        "false": "0",
                    },
                }
            }
            locations = session.post(json_url, headers=headers, json=payload).json()[
                "response"
            ]["collection"]
            for _ in locations:
                street_address = _["address1"]
                if _.get("address2"):
                    street_address += " " + _["address2"]

                hours = []
                for day in days:
                    day = day.lower()
                    if _.get(f"{day}_open") and _.get(f"{day}_open") != "On Call":
                        if _.get(f"{day}_open") == "Closed":
                            times = "closed"
                        else:
                            times = _.get(f"{day}_open") + " - " + _.get(f"{day}_close")
                        hours.append(f"{day}: {times}")

                state = _["state"] if _.get("state") else _.get("province")
                if state:
                    state = state.replace(",", " ").strip()
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    locator_domain=locator_domain,
                    street_address=street_address,
                    city=_["city"].split(",")[0].strip() if _["city"] else "",
                    state=state,
                    zip_postal=_.get("postalcode"),
                    country_code=_["country"],
                    phone=_.get("phone").split("X")[0] if _.get("phone") else "",
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
