from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ch")

locator_domain = "https://www.timberland.de"
locator_url = (
    "https://hosted.where2getit.com/timberland/timberlandeu/index_de.newdesign.html"
)

json_url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch?like=0.05419636461621935&lang=de_DE"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
}


def fetch_records(search, token):
    for lat, lng in search:
        current_country = search.current_country()
        with SgRequests(proxy_country="de") as http:
            payload = {
                "request": {
                    "appkey": token,
                    "formdata": {
                        "geoip": "false",
                        "dataview": "store_default",
                        "atleast": 1,
                        "limit": 250,
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": "",
                                    "country": current_country.upper(),
                                    "latitude": str(lat),
                                    "longitude": str(lng),
                                    "state": "",
                                    "province": "",
                                    "city": "",
                                    "address1": "",
                                    "postalcode": "",
                                }
                            ]
                        },
                        "searchradius": "1000",
                        "radiusuom": "km",
                        "order": "retail_store,outletstore,authorized_reseller,_distance",
                        "where": {
                            "or": {
                                "retail_store": {"eq": ""},
                                "outletstore": {"eq": ""},
                                "icon": {"eq": ""},
                            },
                            "and": {
                                "service_giftcard": {"eq": ""},
                                "service_clickcollect": {"eq": ""},
                                "service_secondchance": {"eq": ""},
                                "service_appointment": {"eq": ""},
                                "service_reserve": {"eq": ""},
                                "service_onlinereturns": {"eq": ""},
                                "service_orderpickup": {"eq": ""},
                                "service_virtualqueuing": {"eq": ""},
                                "service_socialpage": {"eq": ""},
                                "service_eventbrite": {"eq": ""},
                                "service_storeevents": {"eq": ""},
                                "service_whatsapp": {"eq": ""},
                            },
                        },
                        "false": "0",
                    },
                }
            }

            try:
                locations = http.post(json_url, headers=headers, json=payload).json()[
                    "response"
                ]
            except:
                continue
            if "collection" in locations:
                search.found_location_at(lat, lng)

                locations = locations["collection"]
                logger.info(f"[{current_country}] {lat, lng} {len(locations)}")
                for _ in locations:
                    location_name = " ".join(
                        bs(_["name"], "lxml").stripped_strings
                    ).replace("&reg;", "®")
                    street_address = _["address1"]
                    if _["address2"]:
                        street_address += " " + _["address2"]
                    if _["address3"]:
                        street_address += " " + _["address3"]
                    location_type = "Timberland Outlet"
                    if _["retail_store"]:
                        location_type = "Timberland Store"

                    hours = _["hours_de"]
                    if hours and "Bitte rufen Sie im Ladengesch" in hours:
                        hours = ""
                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url="https://www.timberland.de/utility/handlersuche.html",
                        location_name=location_name,
                        street_address=street_address,
                        city=_.get("city"),
                        state=_.get("state"),
                        zip_postal=_.get("postalcode"),
                        country_code=_.get("country"),
                        store_number=_.get("uid"),
                        phone=_["phone"],
                        latitude=_["latitude"],
                        longitude=_["longitude"],
                        location_type=location_type,
                        hours_of_operation=hours,
                    )
            else:
                pass


if __name__ == "__main__":
    with SgRequests(verify_ssl=False) as http:
        token = bs(http.get(locator_url, headers=headers).text, "lxml").select_one(
            "script#brandifyjs"
        )["data-a"]
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=150
            )
        ) as writer:
            search = DynamicGeoSearch(
                country_codes=SearchableCountries.ALL, granularity=Grain_8()
            )

            for rec in fetch_records(search, token):
                writer.write_row(rec)
