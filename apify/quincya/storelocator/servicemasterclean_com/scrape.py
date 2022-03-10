import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("servicemasterclean_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.servicemasterclean.com/locations/?CallAjax=GetLocations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.servicemasterclean.com"

    session = SgRequests()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=250,
        expected_search_radius_miles=250,
    )

    found = []
    for postcode in search:
        json = {
            "zipcode": postcode,
            "distance": "250",
            "tab": "ZipSearch",
            "templates": {
                "Item": '&lt;li data-servicetype="[{ServiceTypeIDs}]" data-serviceid="[{ServiceIDs}]"&gt;\t&lt;h2&gt;{FranchiseLocationName}&lt;/h2&gt;\t&lt;div class="info flex"&gt;\t\t&lt;if field="GMBLink"&gt;\t\t\t&lt;span class="rating-{FN0:GMBReviewRatingScoreOutOfFive}"&gt;\t\t\t\t{FN1:GMBReviewRatingScoreOutOfFive}\t\t\t\t&lt;svg data-use="star.36" class="rate1"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate2"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate3"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate4"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate5"&gt;&lt;/svg&gt;\t\t\t&lt;/span&gt;\t\t\t&lt;a href="{http:GMBLink}" target="_blank"&gt;Visit Google My Business Page&lt;/a&gt;\t\t&lt;/if&gt;\t\t&lt;if field="YelpLink"&gt;\t\t\t&lt;span class="rating-{FN0:YelpReviewRatingScoreOutOfFive}"&gt;\t\t\t\t{FN1:YelpReviewRatingScoreOutOfFive}\t\t\t\t&lt;svg data-use="star.36" class="rate1"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate2"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate3"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate4"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate5"&gt;&lt;/svg&gt;\t\t\t&lt;/span&gt;\t\t\t&lt;a href="{http:YelpLink}" target="_blank"&gt;Visit Yelp Page&lt;/a&gt;\t\t&lt;/if&gt;\t\t&lt;a class="flex" href="tel:{Phone}"&gt;\t\t\t&lt;svg data-use="phone.36"&gt;&lt;/svg&gt; {F:P:Phone}\t\t&lt;/a&gt;\t\t&lt;if field="Path"&gt;\t\t\t&lt;a href="{Path}" class="text-btn" rel="nofollow noopener"&gt;Website&lt;/a&gt;\t\t&lt;/if&gt;\t&lt;/div&gt;\t&lt;div class="type flex"&gt;\t\t&lt;strong&gt;Services:&lt;/strong&gt;\t\t&lt;ul&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2638"&gt;\t\t\t\t&lt;li&gt;Commercial&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2658"&gt;\t\t\t\t&lt;li&gt;Residential&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2634"&gt;\t\t\t\t&lt;li&gt;Janitorial&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t&lt;/ul&gt;\t&lt;/div&gt;&lt;/li&gt;'
            },
        }
        stores = session.post(base_link, headers=headers, json=json).json()

        for store in stores:
            try:
                location_name = store["FranchiseLocationName"]
            except:
                continue
            try:
                street_address = (store["Address1"] + " " + store["Address2"]).strip()
            except:
                street_address = store["Address1"]
            city = store["City"]
            state = store["State"]
            zip_code = store["ZipCode"]
            country_code = store["Country"]
            phone = store["Phone"]
            location_type = store["LocationType"]
            latitude = store["Latitude"]
            longitude = store["Longitude"]
            search.found_location_at(latitude, longitude)
            store_number = store["FranchiseLocationID"]
            hours_of_operation = store["LocationHours"]
            link = locator_domain + store["Path"]

            if link not in found:
                logger.info(link)
                found.append(link)

                try:
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")
                except:
                    session = SgRequests()
                    time.sleep(10)
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")

                if (
                    "COMING SOON" in base.h1.text.upper()
                    or "COMING SOON" in base.title.text.upper()
                ):
                    continue

                try:
                    store_number = base.find(class_="box")["data-key"]
                except:
                    pass

                try:
                    if base.find(id="HoursContainer").text.strip():
                        try:
                            payload = {
                                "_m_": "HoursPopup",
                                "HoursPopup$_edit_": store_number,
                            }

                            response = session.post(link, headers=headers, data=payload)
                            hr_base = BeautifulSoup(response.text, "lxml")
                            hours_of_operation = " ".join(
                                list(hr_base.table.stripped_strings)
                            )
                        except:
                            hours_of_operation = "<MISSING>"
                except:
                    pass

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
