import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import unicodedata

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=200,
    )
    address = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": "https://www.bmwusa.com/?bmw=grp:BMWcom:header:nsc-flyout",
    }
    for zip_code in search:
        result_coords = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }
        location_url = (
            "https://www.careeronestop.org/Localhelp/AmericanJobCenters/find-american-job-centers.aspx?&location="
            + str(zip_code)
            + "&radius=100&pagesize=100"
        )
        try:
            r = session.get(location_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            table = (
                soup.find("table", {"class": "cos-table cos-table-mobile"})
                .find("tbody")
                .find_all("tr")
            )
        except:
            pass
        for tr in table:
            location_name = tr.find("a", {"class": "notranslate"}).text
            page_url = tr.find("a", {"class": "notranslate"})["href"]
            raw_data = list(tr.find_all("td")[2].stripped_strings)
            hoo = (
                raw_data[2]
                .replace("Hours:", "")
                .strip()
                .replace("  (By appointment only)", "")
                .replace(", Saturday by appointment", "")
                .replace("; open Saturdays and Sundays by appointment only", "")
                .replace("available by phone and email ", "")
                .replace(" Tollesboro Elementary", "")
                .replace(
                    "( No Workforce Center offices are open to the public at this time).",
                    "",
                )
                .replace(
                    "; Scheduled Appointments and Self Service Computer Access only on Fridays",
                    "",
                )
                .replace("; Wednesday evening hours available by appointment", "")
                .replace(
                    "  Virtual services provided during these hours.  Not open to the public.",
                    "",
                )
                .replace("By Appointment Only", "")
                .replace("By appointment  at this time due to COVID", "")
            )
            hoo = (
                hoo.replace("(limited services after 5:00 pm)", "")
                .replace("(except State of Oklahoma holidays)", "")
                .replace("EXCEPT HOLIDAYS", "")
                .replace(
                    "*Operating hours may be different due to COVID-19/Pandemic", ""
                )
                .replace("(Except Holidays)", "")
                .replace("(when school`s in session)", "")
                .replace(
                    "since (COVID-19) AJCC Appointment Only, hours of operation:", ""
                )
                .replace("(Computers Close 15min Prior )", "")
                .replace(", Evenings: By Appointment", "")
                .replace("; Fri. Appointment Only", "")
                .replace("(evening/week: hours available by appointment", "")
                .replace("(As of 10-26-2020) ", "")
                .replace(" (CT)", "")
                .replace("COVID Hours of Operation", "")
                .replace("a Due to Covid-19 please call first.", "")
            )
            hoo = (
                hoo.replace("(Central Time)", "")
                .replace("Please call number listed above", "<MISSING>")
                .replace(", by appointment.", "")
                .replace(", call summer hrs", "")
                .replace("(MT)", "")
                .replace(
                    "(4:00 p.m. after Memorial Day, observed to after Labor Day).", ""
                )
                .replace(" Thu (By Appointment)", "")
                .replace(" CST/ Thursday by appointment", "")
                .replace("(Resource Area closes at 4pm)", "")
                .replace(
                    "Monday and Friday mornings by appointment only at this time.", ""
                )
                .replace(
                    "(currently closed for in-office services; only remote services available)",
                    "",
                )
                .replace(
                    "Closed until further notice due to COVID-19 - call 510-564-0500 for assistance",
                    "<MISSING>",
                )
                .replace(
                    "(facility temporary closed in response to Covid-19; career services are provided remotely)",
                    "",
                )
            )
            hoo = (
                hoo.replace("(uninterrupted service", "")
                .replace(
                    "Virtually (Phone, computer, email, appointments for program participants)",
                    "",
                )
                .replace("Thur (By Appointment)", "")
                .replace(", excluding weekends and holidays", "")
            )
            if hoo == "":
                hoo = "<MISSING>"
            if (
                "Business Rep: No" == hoo
                or "by appointment only" == hoo
                or "Appointment Only" == hoo
                or "Closed to the public" == hoo
                or "By appointment only" == hoo
                or "Call for hours" == hoo
                or "Currently closed due to COVID crisis, some programs available."
                == hoo
                or ", call summer hrs" == hoo
                or "As Needed" == hoo
                or "The Douglas CRC is closed to the public until further notice" == hoo
                or "COVID Hours of Operation " == hoo
                or "N/A" == hoo
            ):
                hoo = "<MISSING>"
            hoo = (
                hoo.replace(
                    "*Operating hours may be different due to COVID-19/Pandemic", ""
                )
                .replace(
                    "since (COVID-19) AJCC Appointment Only, hours of operation:  ", ""
                )
                .replace(
                    "Virtual services provided during these hours.  Not open to the public.",
                    "",
                )
                .replace("COVID Hours of Operation ", "")
                .replace(", Walk-in and appointments available", "")
                .replace("COVID Hours of Operations: Hours of Operation: ", "")
                .replace("Call 940-322-1801 ", "")
                .replace(" call for summer hours", "")
                .replace(
                    "Virtually (Phone, computer, email, appointments for program participants) ",
                    "",
                )
                .replace("Job Service, ", "")
                .replace("Call  -   Hours May Vary", "<MISSING>")
                .replace("varies", "<MISSING>")
                .replace(
                    "During COVID Pandemic Hours of Operation May Change.  Currently open",
                    "",
                )
                .replace(
                    "COVID hours Tuesday and Fridays, by appointment only.", "<MISSING>"
                )
                .replace(
                    " (By appointment only)  Go to www.upperscworks.com  to schedule an appointment.",
                    "",
                )
                .replace(" (except Holidays)", "")
                .replace(
                    " (virtually via phone or email) The Center is open for a limited number of in-person services by appointment only.",
                    "",
                )
                .replace(" (EST)", "")
                .replace("@ ", "")
                .replace(" for lunch", "")
                .replace("  Resource Room is currently closed due to COVID-19", "")
                .replace("Covid Hours by appointment only; Monday - Friday.", "")
                .replace("Call in advance for appointment and hours", "<MISSING>")
            )

            if hoo == "Business Rep: Yes":
                hoo = "<MISSING>"

            temp_phone = (
                raw_data[1]
                .replace("WIOA Office", "")
                .replace("Public Phone:", "")
                .replace("WIOA", "")
                .replace("(", "")
                .replace(")", "-")
                .replace("=", "-")
                .replace(" ", "")
                .lstrip("1-")
                .strip()
            )
            phone = temp_phone[:12].replace("800-285-WORK", "<MISSING>")
            try:
                data_link = "https://www.careeronestop.org/" + page_url
                r1 = session.get(data_link, headers=headers)
                soup = BeautifulSoup(r1.text, "lxml")
                addr = soup.find_all("script", {"type": "text/javascript"})[8]
                data_main = (
                    str(addr)
                    .split("locinfo =")[1]
                    .split("var mapapi")[0]
                    .replace(";", "")
                    .strip()
                )
            except:
                pass

            json_data = json.loads(data_main)
            city = json_data["CITY"]
            street_address1 = json_data["ADDRESS1"]
            state = json_data["STATE"]
            zipp = json_data["ZIP"]
            latitude = json_data["LAT"]
            longitude = json_data["LON"]
            result_coords.append((latitude, longitude))
            location_name = soup.find("div", {"id": "detailsheading"}).text
            st_data = (
                soup.find_all("span", {"class": "notranslate"})[2]
                .text.split(",")[0]
                .replace(street_address1, "")
            )
            street_address = (
                street_address1
                + " "
                + st_data.replace("  Square Shopping Center", "")
                .replace(
                    "Due to tornado using Columbia center address. No new location at this time",
                    "",
                )
                .replace("An Illinois workNet Center", "")
                .replace("An Illinois workNet Partner", "")
                .replace(str(city), "")
            )
            street_address = (
                street_address.replace("(Bob Hope Patriotic Hall)", "")
                .replace(", Los Angeles CA 90011 (Primary Site) 1006 E 28th", "")
                .replace("(Zip Code 72957)", "")
                .replace("(71914)", "")
                .replace("105 East  Avenue", "")
                .replace("(Parking deck)", "")
                .replace("(Butte Co. Dept. of Employment & Social Services)", "")
            )
            street_address = (
                street_address.replace("Valley Corporate DriveBldg. A", "")
                .replace(
                    "Valley Corporate Drive County Health and Human Services Agency Building",
                    "",
                )
                .replace("(25330)", "")
                .replace("(Mailing Address)", "")
                .replace(" 584 Northwest University Boulevard", "")
                .replace(", East 1112 Manatee Avenue", "")
                .replace(" 3050 Horseshoe Drive North", "")
            )
            street_address = (
                street_address.replace("  Market Plaza", " ")
                .replace(" 24025  Freeway", " ")
                .replace("(Mondawmin Mall)", "")
                .replace("(Hamilton Street Entrance)", "")
                .replace("(basement of  City Hall)", "")
                .replace("(Mailing)", "")
                .replace(" - (Satellite of the Employment Office)", "")
                .replace("; Chesapeake Square Shopping Center", "")
                .replace("(45422)", "")
            )
            street_address = (
                street_address.replace(" 313 W. Jefferson  Street", "")
                .replace("(Mail Stop 4RS79)", "")
                .replace("(No Delivery to Physical Address)", "")
                .replace("Free Parking off East 19th", "")
                .replace(" Department of Human Resources", " Room 101")
                .replace(" 6401  BlvdPO ", " ")
                .replace(" 55 Makaena Street", "")
                .replace(" 1505 Dillingham Blvd", "")
            )
            street_address = (
                street_address.replace(" 10 Calle Ramon E. Betances", "")
                .replace(" Calle Palma", "")
                .replace(", Bayamon, PR 00961 #10 Palmer St esq. Dr. Veve St", "")
                .replace("(Civic Center)", "")
                .replace(" 344  Street", " ")
                .replace(", 2325 East 12th Street", "")
            )

            store = []
            store.append("https://www.careeronestop.org/")
            store.append(location_name)
            store.append(
                street_address.replace("      ", " ")
                .replace("7161  Gateway Drive", "")
                .strip()
            )
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hoo if hoo else "<MISSING>")
            store.append(data_link)
            for i in range(len(store)):
                if isinstance(store[i], str):
                    store[i] = "".join(
                        (
                            c
                            for c in unicodedata.normalize("NFD", store[i])
                            if unicodedata.category(c) != "Mn"
                        )
                    )
            store = [x.replace("–", "-") if isinstance(x, str) else x for x in store]
            store = [x.strip() if isinstance(x, str) else x for x in store]
            if store[2] in address:
                pass
            address.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
