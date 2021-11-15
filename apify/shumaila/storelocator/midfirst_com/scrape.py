from sgrequests import SgRequests
from sgselenium import SgSelenium
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import ssl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

ssl._create_default_https_context = ssl._create_unverified_context

session = SgRequests()


def fetch_data():
    mylist = static_coordinate_list(10, SearchableCountries.USA)
    mylist = mylist + [
        ("35.4923225", "-97.5656498"),
        ("35.46438", "-97.58406"),
        ("33.4528335", "-112.0738079"),
    ]

    driver = SgSelenium().chrome()
    addresses = []
    base_url = "https://www.midfirst.com"
    driver.get("https://www.midfirst.com/locations")
    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie["name"]] = cookie["value"]
    cookies_string = (
        str(cookies_json)
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(": ", "=")
        .replace(",", ";")
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "cookie": cookies_string,
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    driver.quit()
    r_token = session.get("https://www.midfirst.com/api/Token/get", headers=headers)
    token_for_post = r_token.json()["Token"]
    token_for_cookie = r_token.headers["Set-Cookie"].split(";")[0] + ";"

    cookies_string = (
        str(cookies_json)
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
        .replace(": ", "=")
        .replace(",", ";")
    )

    final_cookies_string = cookies_string + ";" + token_for_cookie

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "cookie": final_cookies_string,
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
    }

    MAX_RESULTS = 25
    MAX_DISTANCE = 150

    for lat, lng in mylist:
        try:
            json_data = session.post(
                "https://www.midfirst.com/api/Locations",
                headers=headers,
                data="location-banking-center=on&location-atm=on&location-distance="
                + str(MAX_DISTANCE)
                + "&location-count="
                + str(MAX_RESULTS)
                + "&location-lat="
                + str(lat)
                + "&location-long="
                + str(lng)
                + "&__RequestVerificationToken="
                + token_for_post,
            ).json()["FilteredResults"]

            check = len(json_data)
            if check > 0:
                pass
        except:
            continue
        for location in json_data:
            store_number = str(location["Ref"])
            location_name = location["Name"]
            phone = location["PhoneNumber"]
            latitude = str(location["Latitude"])
            longitude = str(location["Longitude"])
            street_address = location["Address1"] + " " + location["Address2"]
            zipp = location["PostalCode"]
            location_type = location["LocationType"]["Name"]
            city = location["City"]["Name"]
            state = location["State"]["Name"]
            link = base_url + location["DetailsPath"]
            hours_of_operation = ""
            for day_hours in location["Schedules"]:
                close = (int)(day_hours["ClosingTime"].split(":")[0])
                if close > 12:
                    close = close - 12
                hours_of_operation += (
                    day_hours["DayOfWeek"]["Name"]
                    + " "
                    + day_hours["OpeningTime"].split(":")[0]
                    + ":"
                    + day_hours["OpeningTime"].split(":")[1]
                    + " AM - "
                    + str(close)
                    + ":"
                    + day_hours["ClosingTime"].split(":")[1]
                    + " PM "
                )
            if street_address in addresses:
                continue
            if (len(phone)) < 3:
                phone = "<MISSING>"
            if len(hours_of_operation) < 3:
                hours_of_operation = "<MISSING>"
            yield SgRecord(
                locator_domain=base_url,
                page_url=link,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zipp.strip(),
                country_code="US",
                store_number=str(store_number),
                phone=phone.strip(),
                location_type=location_type,
                latitude=str(latitude),
                longitude=str(longitude),
                hours_of_operation=hours_of_operation,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
