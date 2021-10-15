from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "dime.com"

    for num in range(5):
        base_link = (
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=4d147fbde2e86f7e704b7dc167e721bc&jsLibVersion=v1.7.1&sessionTrackingEnabled=true&input=&experienceKey=dime&version=PRODUCTION&filters=%7B%7D&facetFilters=%7B%7D&verticalKey=locations&limit=20&offset="
            + str(num * 20)
            + "&retrieveFacets=true&locale=en&queryTrigger=initialize&referrerPageUrl=&source=STANDARD"
        )
        stores = session.get(base_link, headers=headers).json()["response"]["results"]

        for i in stores:
            store = i["data"]
            try:
                location_name = store["geomodifier"].replace("\xa0", " ")
            except:
                location_name = store["name"].replace("\xa0", " ")
            if "- CLOSED" in location_name.upper():
                continue
            street_address = store["address"]["line1"]
            city = store["address"]["city"]
            state = store["address"]["region"]
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["countryCode"]
            store_number = store["id"]
            try:
                phone = store["mainPhone"]
            except:
                phone = ""
            try:
                location_type = ",".join(store["services"])
            except:
                location_type = "<MISSING>"
            try:
                raw_hours = store["hours"]
                hours_of_operation = ""
                for raw_hour in raw_hours:
                    try:
                        end = raw_hours[raw_hour]["openIntervals"][0]["end"]
                        start = raw_hours[raw_hour]["openIntervals"][0]["start"]
                        hours_of_operation = (
                            hours_of_operation
                            + " "
                            + raw_hour
                            + " "
                            + start
                            + "-"
                            + end
                        ).strip()
                    except:
                        hours_of_operation = (
                            hours_of_operation + " " + raw_hour + " Closed"
                        ).strip()
            except:
                hours_of_operation = "<MISSING>"

            try:
                geo = store["geocodedCoordinate"]
            except:
                geo = store["yextDisplayCoordinate"]
            latitude = geo["latitude"]
            longitude = geo["longitude"]
            try:
                link = store["website"]
            except:
                link = "https://answers.dime.com/locations.html?tabOrder=.%2Findex.html%2Cfaqs%2Clocations%2Cmerger_faqs%2Cppp_faqs%2Cproducts&referrerPageUrl=https%3A%2F%2Fwww.dime.com%2F"

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
