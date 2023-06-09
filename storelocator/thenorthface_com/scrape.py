from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import SearchableCountries, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Host": "hosted.where2getit.com",
    "Origin": "https://hosted.where2getit.com",
    "Referer": "https://hosted.where2getit.com/northface/2015/index.html",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
}

locator_domain = "https://www.thenorthface.com"
us_app_key_url = "https://hosted.where2getit.com/northface/2015/index.html"


def get_us_app_key():
    with SgRequests() as session:
        app_key_request = session.get(us_app_key_url)
        app_key_soup = bs(app_key_request.text, "lxml")
        app_key = "C1907EFA-14E9-11DF-8215-BBFCBD236D0E"
        for script in app_key_soup.find_all("script"):
            if "appkey: " in script.text:
                app_key = (
                    script.text.split("appkey: ")[1].split(",")[0].replace("'", "")
                )
                break

        return app_key


class ExampleSearchIteration(SearchIteration):
    def __init__(self, app_key):
        self.app_key = app_key

    def do(
        self,
        coord,
        zipcode,
        current_country,
        items_remaining,
        found_location_at,
    ):
        with SgRequests() as session:
            payload = {
                "request": {
                    "appkey": self.app_key,
                    "formdata": {
                        "geoip": "false",
                        "dataview": "store_default",
                        "limit": "300",
                        "order": "rank, _DISTANCE",
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": str(zipcode),
                                    "country": "US",
                                    "latitude": "",
                                    "longitude": "",
                                    "state": "",
                                    "province": "",
                                    "city": "",
                                    "address1": "",
                                    "postalcode": str(zipcode),
                                }
                            ]
                        },
                        "searchradius": "200",
                        "where": {
                            "visiblelocations": {"eq": ""},
                            "or": {
                                "northface": {"eq": ""},
                                "outletstore": {"eq": ""},
                                "retailstore": {"eq": ""},
                                "summit": {"eq": ""},
                            },
                            "and": {
                                "youth": {"eq": ""},
                                "apparel": {"eq": ""},
                                "footwear": {"eq": ""},
                                "equipment": {"eq": ""},
                                "mt": {"eq": ""},
                                "access_pack": {"eq": ""},
                                "steep_series": {"eq": ""},
                                "vectiv": {"eq": ""},
                                "ski_snowboard": {"eq": ""},
                            },
                        },
                        "false": "0",
                    },
                }
            }
            r = session.post(
                "https://hosted.where2getit.com/northface/2015/rest/locatorsearch?lang=en_EN",
                headers=headers,
                json=payload,
            )
            if "collectioncount" not in r.json()["response"]:
                return None

            locations = r.json()["response"]["collection"]
            logger.info(f"[{current_country}] found: {len(locations)}")
            for _ in locations:
                page_url = "https://www.thenorthface.com/utility/store-locator.html"
                storekey = _["clientkey"]
                if storekey and "USA" in storekey:
                    page_url = (
                        "https://stores.thenorthface.com/"
                        + "".join(_["state"]).lower()
                        + "/"
                        + "".join(_["city"]).replace(" ", "-").lower()
                        + "/"
                        + storekey
                    )
                street_address = ""
                if _["address1"] is not None:
                    street_address = street_address + _["address1"]
                if _["address2"] is not None:
                    street_address = street_address + _["address2"]

                state = _["state"] if _["country"] == "US" else _["province"]
                location_type = "the north face"
                north_store = _.get("northface")
                if north_store == "1":
                    location_type = "the north face store"
                outlet_store = _.get("outletstore")
                if outlet_store == "1":
                    location_type = "the north face outletstore"

                phone = (
                    _["phone"].split("or")[0].split(";")[0].split("and")[0]
                    if _["phone"] is not None and _["phone"] != "TBD"
                    else "<MISSING>"
                )

                hours = ""
                if _["m"] is not None:
                    hours = hours + " Monday " + _["m"]
                if _["t"] is not None:
                    hours = hours + " Tuesday " + _["t"]
                if _["w"] is not None:
                    hours = hours + " Wednesday " + _["w"]
                if _["thu"] is not None:
                    hours = hours + " Thursday " + _["thu"]
                if _["f"] is not None:
                    hours = hours + " Friday " + _["f"]
                if _["sa"] is not None:
                    hours = hours + " Saturday " + _["sa"]
                if _["su"] is not None:
                    hours = hours + " Sunday " + _["su"]

                found_location_at(_["latitude"], _["longitude"])
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=state,
                    zip_postal=_["postalcode"],
                    country_code=_["country"],
                    phone=phone,
                    location_type=location_type,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgRequests() as session:
        app_key = get_us_app_key()
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            search_maker = DynamicSearchMaker(
                search_type="DynamicZipSearch", granularity=Grain_4()
            )
            search_iter = ExampleSearchIteration(app_key=app_key)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[SearchableCountries.USA],
            )

            for rec in par_search.run():
                if rec:
                    writer.write_row(rec)
