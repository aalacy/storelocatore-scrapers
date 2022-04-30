from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import sglog

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name="gabesstores_com")


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }
    base_url = "https://www.gabesstores.com"
    url_list = []
    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=50,
    )
    for zipcode in zipcodes:

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        location_url = (
            "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=500&location="
            + zipcode
            + "&limit=50&api_key=56bb34af25f122cb7752babc1c8b9767&v=20181201&resolvePlaceholders=true&entityTypes=location&savedFilterIds=39353311"
        )
        k = session.get(location_url, headers=headers).json()
        for i in k["response"]["entities"]:
            street_address = i["address"]["line1"]
            city = i["address"]["city"]
            state = i["address"]["region"]
            zipp = i["address"]["postalCode"]
            location_name = i["name"]
            if "Gabe's - Closed" in location_name or "Gabe's - CLOSED" in location_name:
                continue
            try:
                phone = i["mainPhone"]
            except:
                phone = "<MISSING>"
            latitude = i["yextDisplayCoordinate"]["latitude"]
            longitude = i["yextDisplayCoordinate"]["longitude"]
            zipcodes.found_location_at(latitude, longitude)
            time = ""
            if "landingPageUrl" in i:
                page_url = i["landingPageUrl"]
                if page_url == "https://www.gabesstores.com/":
                    continue

                if page_url not in url_list:
                    url_list.append(page_url)
                    log.info(page_url)
                    k1 = session.get(page_url, headers=headers)
                    soup2 = BeautifulSoup(k1.text, "lxml")
                    time = " ".join(
                        list(
                            soup2.find(
                                "tbody", {"class": "hours-body"}
                            ).stripped_strings
                        )
                    )
                else:
                    continue
            else:
                page_url = "<MISSING>"
            store_number = i["meta"]["id"]

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=time,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
