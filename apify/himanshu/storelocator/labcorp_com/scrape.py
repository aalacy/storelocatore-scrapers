import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("labcorp_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=25,
        max_search_results=200,
    )
    MAX_DISTANCE = 200
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.labcorp.com/"
    for lat, long in search:
        result_coords = []
        location_url = (
            "https://www.labcorp.com/labs-and-appointments/results?lat="
            + str(lat)
            + "&lon="
            + str(long)
            + "&radius="
            + str(MAX_DISTANCE)
        )
        try:
            r = session.get(location_url, headers=headers)
        except:
            r = ""
            pass
        soup = BeautifulSoup(r.text, "html5lib")
        data = soup.find("script", {"type": "application/json"}).text
        json_data = json.loads(data)
        if "lc_psc_locator" in json_data:
            if "psc_locator_app" in json_data["lc_psc_locator"]:
                for i in json_data["lc_psc_locator"]["psc_locator_app"]["settings"][
                    "labs"
                ]:
                    location_name = (
                        i["name"]
                        .replace("-APPOINTMENT ONLY", "")
                        .replace("- APPOINTMENT ONLY", "")
                        .replace("- APPT.  RECOMMENDED", "")
                        .replace("SATURDAY BY APPT. ONLY", "")
                        .replace("- APOINTMENT ONLY", "")
                    )
                    store_number = re.sub(r"\s+", " ", str(i["locatorId"]))
                    street_address = re.sub(r"\s+", " ", i["address"]["street"])
                    city = re.sub(r"\s+", " ", i["address"]["city"])
                    state = re.sub(r"\s+", " ", i["address"]["stateAbbr"])
                    zipp = re.sub(r"\s+", " ", str(i["address"]["postalCode"]))
                    phone = re.sub(r"\s+", " ", str(i["phone"]))
                    latitude = re.sub(r"\s+", " ", str(i["address"]["lat"]))
                    longitude = re.sub(r"\s+", " ", str(i["address"]["lng"]))
                    hours_of_operation = re.sub(
                        r"\s+",
                        " ",
                        i["hours"]
                        .replace("THIS PSC DOES NOT PERFORM URINE OTS COLLECTIONS", "")
                        .replace(
                            "***THIS LOCATION TEMPORARILY CLOSED UNTIL 03-31-2020***",
                            "",
                        )
                        .replace("***NO GLUCOSE TESTING AT THIS SITE ***", "")
                        .replace("DRUG SCREENS ARE NOT PERFORMED AT THIS LOCATION", "")
                        .replace("DRUG SCREENS STOP 1HR BEFORE CLOSING", "")
                        .replace("DRUG SCREENS TAKEN UP TO 1 HOUR PRIOR TO CLOSING", "")
                        .replace("WE ARE INSIDE  THE HOSPITAL", "")
                        .replace(
                            "LOCATED IN MEDICAL OFF EAST 2ND FLR USE ELEVATOR C", ""
                        )
                        .replace(
                            "NO DRUG SCREE N COLLECTIONS SATURDAY 8:00A-12:00P NO DRUG SCREE N COLLECTIONS SEMEN ANALYSI 8A-11A",
                            "",
                        )
                        .replace("PATIENT PAYS FOR PARKING", "")
                        .replace(
                            "GTT TESTING IS ONLY PERFORMED IN THE MORNING SCHEDULE ACCORDINGLY",
                            "",
                        )
                        .replace(
                            "SEMEN ANALYSIS ACCEPTED M-FR DRUG SCREENS NOT PERFORMED AT THIS SITE",
                            "",
                        )
                        .replace(
                            "SEMEN ANALYSIS ACCEPTED M-FR DRUG SCREENS NOT PERFORMED AT THIS SITE",
                            "",
                        )
                        .replace("NO LUNCH", "")
                        .replace("NOON", "PM")
                        .replace("***UPPER DUBLIN***", "")
                        .replace("NO DRUG SCRNS", "")
                        .replace("DRUG SCREENS BY APT ONLY", "")
                        .replace("NO URINE DRUG  NO BIOMETRICS", "")
                        .replace("DRUG SCREENS STOP 1 HOUR PRIOR TO CLOSING", "")
                        .replace("DRUG SCREENS TAKEN 1 HOUR PRIOR TO CLOSE", "")
                        .replace("   SPECIALISTS IN PEDIATRICS", "")
                        .replace("APPT FOR GTT OVER 1 HOUR", "")
                        .replace("APPT REQUIRED FOR GTT TEST OVER 1 HOUR", "")
                        .replace("THIS SITE SPECIALIZES IN PEDIATRICS", "")
                        .replace("LOCATED IN PROMENADE PENINSULA 3RD FLOOR", "")
                        .replace("APPOINTMENT ONLY********* ", "")
                        .replace("NO SALIVA ALCOHOL TESTS", "")
                        .replace("**SITE CLOSED FRIDAY 8-30-19**", "")
                        .replace("APPOINTMENT IS RECOMMENDED : ", "")
                        .replace("NO EMPLOYER  WELLNESS  SCREENING", "")
                        .replace("  THIS PSC COLLECTS URINE DRUG SCREENS ONLY", "")
                        .replace("*PLEASE VISIT NEAREST OPEN LOCATION*", "")
                        .replace(
                            " ROUTINE BLOOD  WORK ONLY LIMITED  SERVICE-CALL  FOR DETAILS",
                            "",
                        )
                        .replace(" LIMITED  SERVICES CALL  FOR DETAILS", "")
                        .replace("LIMITED  SERVICE CALL  FOR DETAILS", "")
                        .replace("NO DRUG TESTING AND LIMITED SERVICES", "")
                        .replace(
                            "NO OCCUPATIONAL DRUG SCREENING COLLECTIONS OFFERED AT THIS SITE",
                            "",
                        )
                        .replace(
                            "DRUG SCREENS ONLY BY APPOINTMENT NO BLOOD COLLECTION", ""
                        )
                        .replace(
                            "DRUG SCREENS ONLY BY APPOINTMENT NO BLOOD COLLECTION", ""
                        )
                        .replace("NO DRUG SCREENS PERFORMED AT THIS LOCATION", ""),
                    )
                    result_coords.append((latitude, longitude))
                    store = []
                    store.append(base_url)
                    store.append(
                        location_name.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if location_name
                        else "<MISSING>"
                    )
                    store.append(
                        street_address.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if street_address
                        else "<MISSING>"
                    )
                    store.append(
                        city.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if city
                        else "<MISSING>"
                    )
                    store.append(
                        state.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if state
                        else "<MISSING>"
                    )
                    store.append(
                        zipp.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if zipp
                        else "<MISSING>"
                    )
                    store.append("US")
                    store.append(store_number if store_number else "<MISSING>")
                    store.append(
                        phone.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if phone
                        else "<MISSING>"
                    )
                    store.append("<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(
                        str(longitude).replace("\n", "") if longitude else "<MISSING>"
                    )
                    store.append(
                        hours_of_operation.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if hours_of_operation
                        else "<MISSING>"
                    )
                    store.append(
                        "<MISSING>".strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                    )
                    if store[1] + store[2] + store[5] in addresses:
                        continue
                    addresses.append(store[1] + store[2] + store[5])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
