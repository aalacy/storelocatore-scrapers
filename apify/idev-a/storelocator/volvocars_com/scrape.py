from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/"
base_url = "https://www.volvocars.com/api/dealer-locator/dealers/&v=20220124&location={}&radius=1000&countryBias=US&entityTypes=Location&languages=en&filter=%7B%22closed%22:%7B%22$eq%22:false%7D%7D&limit=10&offset=0&fields=name,address,mainPhone,hours,yextDisplayCoordinate,c_activeDealer,c_volvoDealer,c_customWebsite,c_newCarLocator,c_uCLURL,c_scheduleService,c_localOffers,c_servicePartsOffersWebsite,c_servicePartsOffersTrackingTag,c_serviceCenterPhoneNumber,c_partsPhoneNumber2,c_dealerSiteTrackingTag&randomization=0/"


def fetch_records(http, search):
    for zip in search:
        locations = http.get(base_url.format(zip), headers=_headers).json()["response"][
            "entities"
        ]
        logger.info(f"[{zip}] {len(locations)}")
        for _ in locations:
            addr = _["address"]
            latitude = _["yextDisplayCoordinate"]["latitude"]
            longitude = _["yextDisplayCoordinate"]["longitude"]
            search.found_location_at(latitude, longitude)
            hours = []
            for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]:
                day = day.lower()
                for key, hh in _.get("hours", {}).items():
                    times = []
                    if day == key:
                        if hh.get("isClosed"):
                            times = ["closed"]
                        else:
                            for hr in hh["openIntervals"]:
                                times.append(f"{hr['start']} - {hr['end']}")
                        hours.append(f"{day}: {', '.join(times)}")

            page_url = "https://www.volvocarssouthbay.com/"
            if _.get("c_dealerSiteTrackingTag"):
                page_url += _["c_dealerSiteTrackingTag"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["meta"]["id"],
                street_address=addr["line1"],
                city=addr["city"],
                state=addr["region"],
                zip_postal=addr["postalCode"],
                country_code=addr["countryCode"],
                phone=_.get("mainPhone"),
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
