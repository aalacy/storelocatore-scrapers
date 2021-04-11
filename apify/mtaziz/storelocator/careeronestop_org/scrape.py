from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import csv
import unicodedata
from time import sleep
from lxml import html

logger = SgLogSetup().get_logger(logger_name="careeronestop_org")
session = SgRequests()
locator_domain_url = "https://www.careeronestop.org"


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
                row[11].strip(),
                row[12].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def get_hoo(raw_data):
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
        .replace("*Operating hours may be different due to COVID-19/Pandemic", "")
        .replace("(Except Holidays)", "")
        .replace("(when school`s in session)", "")
        .replace("since (COVID-19) AJCC Appointment Only, hours of operation:", "")
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
        .replace("(4:00 p.m. after Memorial Day, observed to after Labor Day).", "")
        .replace(" Thu (By Appointment)", "")
        .replace(" CST/ Thursday by appointment", "")
        .replace("(Resource Area closes at 4pm)", "")
        .replace("Monday and Friday mornings by appointment only at this time.", "")
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
        or "Currently closed due to COVID crisis, some programs available." == hoo
        or ", call summer hrs" == hoo
        or "As Needed" == hoo
        or "The Douglas CRC is closed to the public until further notice" == hoo
        or "COVID Hours of Operation " == hoo
        or "N/A" == hoo
    ):
        hoo = "<MISSING>"
    hoo = (
        hoo.replace("*Operating hours may be different due to COVID-19/Pandemic", "")
        .replace("since (COVID-19) AJCC Appointment Only, hours of operation:  ", "")
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
        .replace("COVID hours Tuesday and Fridays, by appointment only.", "<MISSING>")
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
    hoo = hoo.replace("â€“", "-").replace("a€“", "-")
    return hoo


def get_street_address(st_data_r2, street_address1, city):
    st_data = st_data_r2.xpath('//span[@class="notranslate"]/text()')[2]
    st_data = st_data.split(",")[0].replace(street_address1, "")
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
    street_address = (
        street_address.replace("      ", " ").replace("7161  Gateway Drive", "").strip()
    )
    street_address = street_address.replace("(", "").strip()
    if street_address:
        return street_address
    else:
        return "<MISSING>"


def get_phone(raw_data):
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
    if phone:
        return phone
    else:
        return "<MISSING>"


state_list_ela = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "District of Columbia",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]


def fetch_data():
    address = []
    total = 0
    for search_by_state in state_list_ela:
        search_by_state1 = search_by_state.replace(" ", "%20")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }

        location_url = f"https://www.careeronestop.org//Localhelp/AmericanJobCenters/find-american-job-centers.aspx?location={search_by_state1}&radius=100&ct=0&y=0&w=0&e=0&sortcolumns=Location&sortdirections=ASC&curPage=1&pagesize=500"
        logger.info(f"Pulling the Data From: {location_url} \n")
        logger.info(f"Pulling the Data for the State: {search_by_state}")
        r = session.get(location_url, headers=headers)
        sleep(2)
        data_r = html.fromstring(r.text, "lxml")
        ajc_found_in_the_sate = "".join(
            data_r.xpath('//strong[@id="recordNumber"]/text()')
        )
        xpath_tr_data = '//table[@class="cos-table cos-table-mobile"]/tbody/tr'
        data1 = data_r.xpath(xpath_tr_data)
        logger.info(
            f"We found ({ajc_found_in_the_sate}) American Job Centers in {search_by_state}"
        )

        found = 0
        for tr in data1:
            location_name = tr.xpath(
                './td/a[@class="notranslate" and @target="_self"]/text()'
            )
            location_name = "".join(location_name).strip()

            page_url = tr.xpath(
                './td/a[@class="notranslate" and @target="_self"]/@href'
            )
            page_url = "".join(page_url)
            raw_data = tr.xpath("./td[3]//text()")
            logger.info(f"\n Phone and HOO RAW Data: {raw_data}\n")
            try:
                data_link = "https://www.careeronestop.org" + page_url
                logger.info(f"\nPulling the data from: {data_link}\n")
                r2 = session.get(data_link, headers=headers)

                sleep(1)

                data_r2 = html.fromstring(r2.text, "lxml")
                addr = data_r2.xpath('//script[@type="text/javascript"]/text()')
                addr = "".join(addr)
                data_main = (
                    addr.split("locinfo =")[1]
                    .split("var mapapi")[0]
                    .split(";")[0]
                    .strip()
                )
            except:
                pass
            json_data = json.loads(data_main)
            locator_domain = locator_domain_url
            page_url = data_link
            try:
                location_name = data_r2.xpath('//div[@id="detailsheading"]/text()')
                location_name = "".join(location_name)
            except:
                location_name = "<MISSING>"
            logger.info(f"Location Name: {location_name}")
            street_address1 = json_data["ADDRESS1"]
            city = json_data["CITY"]
            street_address = get_street_address(data_r2, street_address1, city)
            city = city if city else "<MISSING>"
            state = json_data["STATE"] if json_data["STATE"] else "<MISSING>"
            zip = json_data["ZIP"] if json_data["ZIP"] else "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = get_phone(raw_data)
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = json_data["LAT"] if json_data["LAT"] else "<MISSING>"
            longitude = json_data["LON"] if json_data["LON"] else "<MISSING>"
            hoo = get_hoo(raw_data)
            hours_of_operation = hoo if hoo else "<MISSING>"
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            for i in range(len(row)):
                if isinstance(row[i], str):
                    row[i] = "".join(
                        (
                            c
                            for c in unicodedata.normalize("NFD", row[i])
                            if unicodedata.category(c) != "Mn"
                        )
                    )

            row = [x.replace("–", "-") if isinstance(x, str) else x for x in row]
            row = [x.strip() if isinstance(x, str) else x for x in row]
            if row not in address:
                address.append(row)
            else:
                continue
            found += 1
        total += found
        logger.info(f"AJC Cumulative Count as Scraping Goes on: {total}")
    logger.info(f"Total American Job Centers Found: {total}")
    return address


def scrape():
    logger.info("Scraping Started...Please wait until it's finished!!!")
    data = fetch_data()
    logger.info(
        f"\nScraping Finished | Total AJC Found without Duplicates: {len(data)}"
    )
    write_output(data)


if __name__ == "__main__":
    scrape()
