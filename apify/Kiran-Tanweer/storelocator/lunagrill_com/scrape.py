from bs4 import BeautifulSoup
import csv
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lunagrill_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    linklist = []
    url = "https://locations.lunagrill.com/site-map/US"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    info = soup.text
    links = str(soup)
    alldata = links.split('<script defer=""')[1].split(
        "Yext.analyticsEvent = yext.analytics.getYextAnalytics("
    )[0]
    coords = alldata.split("Get Directions")
    for i in coords:
        coordslink = i.split('"drivingdirection" href="')
        if len(coordslink) == 2:
            link = coordslink[1].split('" rel="')[0]
            linklist.append(link)
    info = info.split("Get Directions")
    for j, k in zip(info, linklist):
        title = "Luna Grill"
        hours = j.split('"normalHours"')
        if len(hours) == 2:
            hours = hours[1].split(',"utcOffsets"')[0]
            mon = hours.split('"MONDAY","intervals":[{')[1].split("}],")[0]
            mon_start = mon.split('"start":')[1]
            mon_end = mon.split('"end":')[1].split(",")[0]

            tues = hours.split('"TUESDAY","intervals":[{')[1].split("}],")[0]
            tues_start = tues.split('"start":')[1]
            tues_end = tues.split('"end":')[1].split(",")[0]

            wed = hours.split('"WEDNESDAY","intervals":[{')[1].split("}],")[0]
            wed_start = wed.split('"start":')[1]
            wed_end = wed.split('"end":')[1].split(",")[0]

            thurs = hours.split('"THURSDAY","intervals":[{')[1].split("}],")[0]
            thurs_start = thurs.split('"start":')[1]
            thurs_end = thurs.split('"end":')[1].split(",")[0]

            fri = hours.split('"FRIDAY","intervals":[{')[1].split("}],")[0]
            fri_start = fri.split('"start":')[1]
            fri_end = fri.split('"end":')[1].split(",")[0]

            sat = hours.split('"SATURDAY","intervals":[{')[1].split("}],")[0]
            sat_start = sat.split('"start":')[1]
            sat_end = sat.split('"end":')[1].split(",")[0]

            sun = hours.split('"SUNDAY","intervals":[{')[1].split("}],")[0]
            sun_start = sun.split('"start":')[1]
            sun_end = sun.split('"end":')[1].split(",")[0]

            if mon_start == "1100":
                mon_start = "11:00 AM"
            if tues_start == "1100":
                tues_start = "11:00 AM"
            if wed_start == "1100":
                wed_start = "11:00 AM"
            if thurs_start == "1100":
                thurs_start = "11:00 AM"
            if fri_start == "1100":
                fri_start = "11:00 AM"
            if sat_start == "1100":
                sat_start = "11:00 AM"
            if sun_start == "1100":
                sun_start = "11:00 AM"
            if mon_start == "1030":
                mon_start = "10:30 AM"
            if tues_start == "1030":
                tues_start = "10:30 AM"
            if wed_start == "1030":
                wed_start = "10:30 AM"
            if thurs_start == "1030":
                thurs_start = "10:30 AM"
            if fri_start == "1030":
                fri_start = "10:30 AM"
            if sat_start == "1030":
                sat_start = "10:30 AM"
            if sun_start == "1030":
                sun_start = "10:30 AM"
            if sun_start == "1200":
                sun_start = "12:00 PM"
            if sun_start == "0":
                sun_start = "12:00 AM"
            if mon_end == "2100":
                mon_end = "9:00 PM"
            if tues_end == "2100":
                tues_end = "9:00 PM"
            if wed_end == "2100":
                wed_end = "9:00 PM"
            if thurs_end == "2100":
                thurs_end = "9:00 PM"
            if fri_end == "2100":
                fri_end = "9:00 PM"
            if sat_end == "2100":
                sat_end = "9:00 PM"
            if sun_end == "2100":
                sun_end = "9:00 PM"
            if mon_end == "2030":
                mon_end = "8:30 PM"
            if tues_end == "2030":
                tues_end = "8:30 PM"
            if wed_end == "2030":
                wed_end = "8:30 PM"
            if thurs_end == "2030":
                thurs_end = "8:30 PM"
            if fri_end == "2030":
                fri_end = "8:30 PM"
            if sat_end == "2030":
                sat_end = "8:30 PM"
            if sun_end == "2030":
                sun_end = "8:30 PM"
            if mon_end == "2000":
                mon_end = "8:00 PM"
            if tues_end == "2000":
                tues_end = "8:00 PM"
            if wed_end == "2000":
                wed_end = "8:00 PM"
            if thurs_end == "2000":
                thurs_end = "8:00 PM"
            if fri_end == "2000":
                fri_end = "8:00 PM"
            if sat_end == "2000":
                sat_end = "8:00 PM"
            if sun_end == "2000":
                sun_end = "8:00 PM"
            if sun_end == "1900":
                sun_end = "7:00 PM"
            if mon_end == "1900":
                mon_end = "7:00 PM"
            if tues_end == "1900":
                tues_end = "7:00 PM"
            if wed_end == "1900":
                wed_end = "7:00 PM"
            if thurs_end == "1900":
                thurs_end = "7:00 PM"
            if fri_end == "1900":
                fri_end = "7:00 PM"
            if sat_end == "1900":
                sat_end = "7:00 PM"
            if sun_end == "1800":
                sun_end = "6:00 PM"
            if mon_end == "1930":
                mon_end = "7:30 PM"
            if tues_end == "1930":
                tues_end = "7:30 PM"
            if wed_end == "1930":
                wed_end = "7:30 PM"
            if thurs_end == "1930":
                thurs_end = "7:30 PM"
            if fri_end == "1930":
                fri_end = "7:30 PM"
            if sat_end == "1930":
                sat_end = "7:30 PM"
            if sun_end == "1930":
                sun_end = "7:30 PM"
            HOO = (
                "Monday: "
                + mon_start
                + " - "
                + mon_end
                + " "
                + "Tuesday: "
                + tues_start
                + " - "
                + tues_end
                + " "
                + "Wednesday: "
                + wed_start
                + " - "
                + wed_end
                + " "
                + "Thursday: "
                + thurs_start
                + " - "
                + thurs_end
                + " "
                + "Friday: "
                + fri_start
                + " - "
                + fri_end
                + " "
                + "Saturday: "
                + sat_start
                + " - "
                + sat_end
                + " "
                + "Sunday: "
                + sun_start
                + " - "
                + sun_end
            )
        address = j.split("}]}")
        if len(address) == 2:
            address = address[1].split("USPhone:")[0]
            address = address.replace(",", "")
            address = address.strip()
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            street = street.lstrip()
            street = street.replace(",", "")
            city = city.lstrip()
            city = city.replace(",", "")
            state = state.lstrip()
            state = state.replace(",", "")
            pcode = pcode.lstrip()
            pcode = pcode.replace(",", "")
            phone = j.split("Phone: ")
        if len(phone) == 3:
            phone = phone[1].split("Details:")[0]
            phone = phone.strip()
        coordsurl = k
        lat = coordsurl.split("q=")[1].split(",")[0]
        lng = coordsurl.split(",")[1]

        data.append(
            [
                "https://www.lunagrill.com/",
                "https://locations.lunagrill.com/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                lng,
                HOO,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
