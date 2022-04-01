from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://www.mitsubishicars.com/"
    addressess = []
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
    for zip_code in search:
        try:
            link = (
                "https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode="
                + str(zip_code)
                + "&idealer=false&ecommerce=false"
            )
            json_data = session.get(link, headers=headers).json()
        except:
            continue
        for loc in json_data:
            address = loc["address1"].strip()
            if loc["address2"]:
                address += " " + loc["address2"].strip()
            name = loc["dealerName"].strip()
            city = loc["city"].strip().capitalize()
            try:
                state = loc["state"].strip()
            except:
                state = ""
            zipp = loc["zipcode"]
            phone = loc["phone"].strip()
            country = loc["country"].replace("United States", "US").strip()
            lat = loc["latitude"]
            lng = loc["longitude"]
            search.found_location_at(lat, lng)
            link = loc["dealerUrl"]
            storeno = loc["bizId"]
            page_url = ""
            if link:
                page_url = "http://" + link.lower()
                if (
                    "http://www.verneidemitsubishi.com" in page_url
                    or "http://www.kingautomitsubishi.com" in page_url
                    or "http://www.verhagemitsubishi.com" in page_url
                    or "http://www.sisbarro-mitsubishi.com" in page_url
                    or "http://www.delraymitsu.net" in page_url
                ):
                    hours_of_operation = "<INACCESSIBLE>"
                else:
                    try:
                        r1 = session.get(page_url, headers=headers)
                        soup1 = BeautifulSoup(r1.text, "lxml")
                        got_page = True
                    except:
                        got_page = False
                    if got_page:
                        if soup1.find("div", {"class": "sales-hours"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "sales-hours"}
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find(
                            "ul", {"class": "list-unstyled line-height-condensed"}
                        ):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "ul",
                                        {
                                            "class": "list-unstyled line-height-condensed"
                                        },
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "well border-x"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find("div", {"class": "well border-x"})
                                    .find("table")
                                    .stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "hours-block pad-2x"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "hours-block pad-2x"}
                                    ).stripped_strings
                                )
                            )
                        elif soup1.find("div", {"class": "hoursBox"}):
                            hours_of_operation = " ".join(
                                list(
                                    soup1.find(
                                        "div", {"class": "hoursBox"}
                                    ).stripped_strings
                                )
                            )
                        else:
                            hours_of_operation = "<INACCESSIBLE>"
                    else:
                        hours_of_operation = "<INACCESSIBLE>"
            else:
                hours_of_operation = "<MISSING>"
                page_url = ""

            if city == "Little rock" or city == "Charlottesville":
                page_url = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country)
            store.append(storeno)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            try:
                store.append(hours_of_operation.split("} Sales Hours ")[1])
            except:
                store.append(hours_of_operation)
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [
                str(x)
                .encode("ascii", "replace")
                .decode("ascii")
                .strip()
                .replace("?", "")
                if x
                else "<MISSING>"
                for x in store
            ]
            print("Writing ..")
            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
