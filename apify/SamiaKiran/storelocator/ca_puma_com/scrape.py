import csv
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from datetime import datetime
from sgrequests import SgRequests

website = "ca_puma_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
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
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    data = []
    daylist = {
        "A": "Monday",
        "B": "Tuesday",
        "C": "Wednesday",
        "D": "Thursday",
        "E": "Friday",
        "F": "Saturday",
        "G": "Sunday",
    }
    zips = static_zipcode_list(radius=150, country_code=SearchableCountries.USA)
    if True:
        for zip_code in zips:
            url = (
                "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine="
                + zip_code
                + "&f=json&outFields=*"
            )
            address_list = session.get(url, headers=headers, verify=False).json()[
                "candidates"
            ]
            temp = [address["location"] for address in address_list][0]
            LO = str(round(temp["x"], 5))
            LA = str(round(temp["y"], 5))
            url2 = (
                """https://destinilocators.com/control/9.0.3/panel2Connect.php?productPreset=0&CB=20201210fd38a103c5f334318ec7a3ce&TLL=0&BMB=0
                &GLOG=0&MKTC=0&numPost=0&MKTON=1&NCID=&APO=&UTMC=&VINC=0&DEFCTRY=1&PAGE=&BEC=0&BBM=0&ZIP=&LA="""
                + LA
                + """&LO="""
                + LO
                + """&PROD=&GROUP=
                &STYPE=GROUP&CLIENT=puma&ITER=site-us&RFR=https%3A%2F%2Fdestinilocators.com%2Fpuma%2Fsite-us%2Flocator.php%3F"""
            )

            try:
                loclist = session.get(url2, headers=headers, verify=False).json()[
                    "storeArray"
                ]["val"]
            except Exception as e:
                loclist = session.get(url2, headers=headers, verify=False).json()[
                    "storeArray"
                ]["count"]
                if loclist == 0:
                    continue
                else:
                    log.info(e)
            for loc in loclist:
                title = loc["name"]
                store = loc["s_id"]
                street = loc["add1"]
                city = loc["city"]
                state = loc["state"]
                if not state:
                    state = "<MISSING>"
                pcode = loc["zip"]
                lat = loc["lat"]
                longt = loc["lng"]
                phone = loc["phone"]
                if not phone:
                    phone = "<MISSING>"
                ccode = loc["country"]
                if "CANADA" not in ccode:
                    continue
                location_type = loc["scat"]
                if location_type == 1:
                    location_type = "Store"
                else:
                    location_type = "Outlet"
                hour_list = loc["hours"]
                if hour_list == "":
                    hours = "<MISSING>"
                else:
                    hour_list = hour_list.split("|")
                    hours = ""
                    for hour in hour_list:
                        split_first_letter = hour[0]
                        temp_hour = hour.split(split_first_letter, 1)[1]
                        temp_hour = "-".join([temp_hour[:4], temp_hour[4:8]])
                        temp_hour = temp_hour.split("-")
                        Open = temp_hour[0]
                        Open = Open[0:2] + ":" + Open[2:4]
                        Open = datetime.strptime(Open, "%H:%M")
                        Open = Open.strftime("%I:%M %p")
                        close = temp_hour[1]
                        close = close[0:2] + ":" + close[2:4]
                        close = datetime.strptime(close, "%H:%M")
                        close = close.strftime("%I:%M %p")
                        day = daylist[hour[0]]
                        hours = hours + day + " " + Open + " - " + close + " "
                data.append(
                    [
                        "https://ca.puma.com/",
                        "https://ca.puma.com/en/ca/store",
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "CA",
                        store,
                        phone,
                        location_type,
                        lat,
                        longt,
                        hours,
                    ]
                )
        return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
