from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
import csv


logger = SgLogSetup().get_logger("synovus_com")

session = SgRequests()
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.mapquestapi.com",
    "Referer": "https://www.synovus.com/",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
    "method": "GET",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}


def write_output(data1):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data1:
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
    state_list = ["Alabama", "Florida", "Georgia", "South Carolina", "Tennessee"]
    for state in state_list:
        url = (
            "https://www.mapquestapi.com/search/v2/radius?origin="
            + state
            + "&radius=1000&distanceUnit=dm&hostedData=mqap.36969_Synovus&ambiguities=ignore&key=Gmjtd%7Cluu7n961n1%2Crw%3Do5-ly10h&callback=window.MapManager.processSearchResults&_=1606874485792"
        )
        r = session.get(url, headers=headers, verify=False)
        response = r.text
        data2 = response.split("fields")
        data2.pop(0)

        for loc in data2:
            location = '"fields' + loc
            location = location.rstrip(',"')
            title = location.split('"Name":"', 1)[1].split('"')[0]
            latlng = location.split('"latLng":{', 1)[1].split("}")[0]
            lngt = latlng.split('"lng":', 1)[1].split(",")[0]
            lat = latlng.split('"lat":', 1)[1]
            Phone = location.split('"Phone":"', 1)[1].split('"')[0]
            if Phone == "":
                Phone = "<MISSING>"
            street = location.split('"address":"', 1)[1].split('"')[0]
            city = location.split('"city":"', 1)[1].split('"')[0]
            state = location.split('"state":"', 1)[1].split('"')[0]
            postal = location.split('"postal":"', 1)[1].split('"')[0]
            Monday = location.split('"Monday":"', 1)[1].split('"')[0]
            Mon = ""
            if Monday == "":
                Mon = "Monday: " + "Closed"
            else:
                Mon = "Monday: " + Monday
            Tuesday = location.split('"Tuesday":"', 1)[1].split('"')[0]
            Tues = ""
            if Tuesday == "":
                Tues = "Tuesday: " + "Closed"
            else:
                Tues = "Tuesday: " + Tuesday
            Wednesday = location.split('"Wednesday":"', 1)[1].split('"')[0]
            Wed = ""
            if Wednesday == "":
                Wed = "Wednesday: " + "Closed"
            else:
                Wed = "Wednesday: " + Wednesday
            Thursday = location.split('"Thursday":"', 1)[1].split('"')[0]
            Thurs = ""
            if Thursday == "":
                Thurs = "Thursday: " + "Closed"
            else:
                Thurs = "Thursday: " + Thursday
            friday = location.split('"Friday":"', 1)[1].split('"')[0]
            fri = ""
            if friday == "":
                fri = "friday: " + "Closed"
            else:
                fri = "friday: " + friday
            saturday = location.split('"Saturday":"', 1)[1].split('"')[0]
            sat = ""
            if saturday == "":
                sat = "saturday: " + "Closed"
            else:
                sat = "saturday: " + saturday
            sunday = location.split('"Sunday":"', 1)[1].split('"')[0]
            sun = ""
            if sunday == "":
                sun = "Sunday: " + "Closed"
            else:
                sun = "Sunday: " + sunday
            Hours = (
                Mon
                + ", "
                + Tues
                + ", "
                + Wed
                + ", "
                + Thurs
                + ", "
                + fri
                + ", "
                + sat
                + ", "
                + sun
            )
            if (
                Hours
                == "Monday: , Tuesday: , Wednesday: , Thursday: , Friday: , Saturday: , Sunday: "
            ):
                Hours = "<MISSING>"
            Hours = Hours.rstrip()
            Hours = Hours.lstrip()
            types = location.split('"BankShortName":"', 1)[1].split('"')[0]

            if (
                Hours
                == "Monday: Closed, Tuesday: Closed, Wednesday: Closed, Thursday: Closed, friday: Closed, saturday: Closed, Sunday: Closed"
            ):
                Hours = "Closed"
            data.append(
                [
                    "https://www.synovus.com/",
                    url,
                    title,
                    street,
                    city,
                    state,
                    postal,
                    "US",
                    "<MISSING>",
                    Phone,
                    types,
                    lat,
                    lngt,
                    Hours,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
