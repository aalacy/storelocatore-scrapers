from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, Grain_2
import dirtyjson as json
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("lidl")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.lidl.co.uk"
base_url = "https://www.lidl.co.uk/bundles/retail/dist/scripts/FrontPage.js"
session_url = "https://dev.virtualearth.net/webservices/v1/LoggingService/LoggingService.svc/Log?entry=0&fmt=1&type=3&group=MapControl&name=MVC&version=v8&mkt=en-US&auth={}&jsonp=Microsoft.Maps.NetworkCallbacks.f_logCallbackRequest"
json_url = "{}$select=*,__Distance&$filter=Adresstyp%20eq%201&key={}&$format=json&jsonp=Microsoft_Maps_Network_QueryAPI_2&spatialFilter=nearby({},{},1000)"

lv_log_url = "https://dev.virtualearth.net/webservices/v1/LoggingService/LoggingService.svc/Log?entry=0&fmt=1&type=3&group=MapControl&name=MVC&version=v8&mkt=en-US&auth=Ao9qjkbz2fsxw0EyySLTNvzuynLua7XKixA0yBEEGLeNmvrfkkb3XbfIs4fAyV-Z&jsonp=Microsoft.Maps.NetworkCallbacks.f_logCallbackRequest"


def fetch_records(http, search, country_sessions):
    for lat, lng in search:
        data = country_sessions.get(search.current_country())
        try:
            locations = json.loads(
                http.get(
                    json_url.format(data["url"], data["key"], lat, lng),
                    headers=_headers,
                )
                .text.split("Microsoft_Maps_Network_QueryAPI_2(")[1]
                .strip()[:-1]
            )["d"]["results"]
        except:
            continue
        logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
        for _ in locations:
            hours = []
            if _["OpeningTimes"]:
                for hh in bs(_["OpeningTimes"], "lxml").stripped_strings:
                    if "Early" in hh:
                        break
                    hours.append(hh)

            city = _["Locality"]
            zip_postal = _["PostalCode"]
            if _["CountryRegion"] == "GB":
                zz = zip_postal.split()
                if len(zz) == 2 and len(zz[-1]) <= 3 and len(zz[0]) <= 4:
                    pass
                else:
                    city = _["PostalCode"]
                    zip_postal = _["Locality"]

            search.found_location_at(_["Latitude"], _["Longitude"])
            yield SgRecord(
                store_number=_["EntityID"],
                location_name=_["ShownStoreName"],
                street_address=_["AddressLine"],
                city=city,
                zip_postal=zip_postal,
                country_code=_["CountryRegion"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests(proxy_country="us") as http:
        countries = []
        country_sessions = {}
        json_data = json.loads(
            http.get(base_url, headers=_headers)
            .text.split(",bingMap:")[1]
            .split("}),define")[0]
        )
        for country, key in json_data["DATA_SOURCE_QUERY_KEY"].items():
            if (
                country == "UK"
                or country == "ECI"
                or country == "NIE"
                or country == "test"
            ):
                continue
            cc = country.lower()
            countries.append(cc)
            country_sessions[cc] = dict(
                key=json.loads(
                    http.get(session_url.format(key), headers=_headers)
                    .text.split(
                        "Microsoft.Maps.NetworkCallbacks.f_logCallbackRequest("
                    )[1]
                    .strip()[:-1]
                )["sessionId"],
                url=json_data["DATA_SOURCE_URL"][country],
            )

        # addition
        # lv
        lv_key = json.loads(
            http.get(lv_log_url, headers=_headers)
            .text.split("Microsoft.Maps.NetworkCallbacks.f_logCallbackRequest(")[1]
            .strip()[:-1]
        )["sessionId"]
        country_sessions["lv"] = dict(
            key=lv_key,
            url="https://spatial.virtualearth.net/REST/v1/data/b2565f2cd7f64c759e2b5707b969e8dd/Filialdaten-LV/Filialdaten-lv?",
        )
        countries.append("lv")

        search = DynamicGeoSearch(
            country_codes=list(set(countries)), granularity=Grain_2()
        )
        with SgWriter(
            deduper=SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.STREET_ADDRESS,
                        SgRecord.Headers.CITY,
                        SgRecord.Headers.ZIP,
                    }
                ),
                duplicate_streak_failure_factor=100,
            )
        ) as writer:
            for rec in fetch_records(http, search, country_sessions):
                writer.write_row(rec)
