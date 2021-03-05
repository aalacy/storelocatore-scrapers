from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "jeilearning_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    data = []
    url = "https://jeilearning.com/ow/learning_center/searchCenterByState.do"
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NS",
        "NT",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ]

    if True:
        for state in states:
            myobj = {"keyword": state}
            loclist = session.post(url, data=myobj, headers=headers).json()[
                "franchise_list"
            ]
            if not loclist:
                continue
            for loc in loclist:
                title = loc["CENTER_NAME"]
                phone = loc["PHONE_NUM"]
                if "(Cell)" in phone:
                    phone = phone.split("(Cell)", 1)[0]
                street = loc["ADDRESS"]
                city = loc["CITY_NAME"]
                state = loc["STATE_NAME"]
                pcode = loc["ZIP_CODE"]
                ccode = loc["COUNTRY"]
                longt = loc["LNG"]
                lat = loc["LAT"]
                store = loc["FRANCHISE_IDX"]
                link = loc["URL_DIR"]
                link = "https://jeilearning.com/" + link + "/index.do"
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.find("div", {"class": "info_wrap"})
                hour_list = loclist.find("div", {"class": "cont time"}).find(
                    "ul", {"class": "busi"}
                )
                hour_list = hour_list.findAll("li")
                hours = ""
                for hour in hour_list:
                    day = hour.find("span").text
                    time = hour.text.split(day, 1)[1]
                    hours = hours + day + " " + time + " "
                data.append(
                    [
                        "https://jeilearning.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        store,
                        phone,
                        "<MISSING>",
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
