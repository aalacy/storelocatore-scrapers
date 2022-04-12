import json
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("sherwin-williams_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = session.get("https://www.sherwin-williams.com/store-locator", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    location_types = []
    for option in soup.find("select", {"id": "findstores_selectStoreType"}).find_all(
        "option"
    ):
        location_types.append(option["value"])
    store_id = soup.find("meta", {"name": "CommerceSearch"})["content"].split("_")[-1]
    for script in soup.find_all("script"):
        if "WCParamJS " in str(script):
            catalog_id = (
                str(script)
                .split("catalogId")[1]
                .split(",")[0]
                .replace("'", "")
                .replace('"', "")
                .replace(":", "")
            )
    max_results = 25
    max_distance = 75
    r_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
    }
    for loc_type in location_types:

        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
            max_search_distance_miles=max_distance,
            max_search_results=max_results,
        )
        logger.info("Sgzips for loc_type: %s" % loc_type)

        for x, y in search:
            r_data = (
                "sideBarType=LSTORES&latitude="
                + str(x)
                + "&longitude="
                + str(y)
                + "&radius=75&uom=SMI&abbrv=us&storeType="
                + loc_type
                + "&countryCode=&requesttype=ajax&langId=&storeId="
                + str(store_id)
                + "&catalogId="
                + str(catalog_id)
            )
            r = session.post(
                "https://www.sherwin-williams.com/AjaxStoreLocatorSideBarView?langId=-1&storeId="
                + str(store_id),
                headers=r_headers,
                data=r_data,
            )
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(
                soup.find("script", {"id": "storeResultsJSON"}).contents[0]
            )["stores"]
            for store_data in data:
                lat = store_data["latitude"]
                lng = store_data["longitude"]
                locator_domain = "https://www.sherwin-williams.com"
                location_name = store_data["name"] or "<MISSING>"
                street_address = store_data["address"] or "<MISSING>"
                city = store_data["city"] or "<MISSING>"
                state = store_data["state"] or "<MISSING>"
                postal = store_data["zipcode"] or "<MISSING>"
                country_code = "CA"

                store_num = store_data["url"].split("storeNumber=")[1].split("&")[0]
                if store_num in [
                    "190520",
                    "24921",
                    "627001",
                    "622001",
                    "614502",
                    "621001",
                ]:
                    continue
                phone = store_data["phone"] or "<MISSING>"

                link = "https://www.sherwin-williams.com" + store_data["url"]
                location_request = session.get(
                    link,
                    headers=headers,
                )
                location_soup = BeautifulSoup(location_request.text, "lxml")

                hours = ""
                try:
                    hours = (
                        " ".join(
                            list(
                                location_soup.find(
                                    "div",
                                    {
                                        "class": "cmp-storedetailhero__store-hours-container"
                                    },
                                ).stripped_strings
                            )
                        )
                        .replace("Store Hours", "")
                        .strip()
                    )
                except:
                    pass

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=loc_type,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
