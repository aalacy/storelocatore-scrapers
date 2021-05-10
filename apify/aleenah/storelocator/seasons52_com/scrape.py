from bs4 import BeautifulSoup
import csv
import json
from sgselenium import SgSelenium
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="seasons52.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


driver = SgSelenium().chrome()


def fetch_data():
    # Your scraper here
    data = []
    url = "https://www.seasons52.com/locations/all-locations"
    storelist = []
    driver.get(url)
    log.info(driver.page_source)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    divlist = soup.select("a[href*=locations]")
    
    p = 0

    for div in divlist:
        if p == 0:
            link = (
                "https://www.seasons52.com/locations/fl/sunrise/sunrise-sawgrass/4548"
            )
        else:
            link = "https://www.seasons52.com" + div["href"]

        if link.find("-locations") == -1:
            log.info(link)
            driver.get(link)
            loc = (
                driver.page_source.split('<script type="application/ld+json">', 1)[1]
                .split("</script>", 1)[0]
                .replace("\n", "")
            )

            loc = json.loads(loc)

            if (
                len(loc) > 0
                and loc["address"]
                and loc["address"]["addressLocality"].strip() != ""
                and loc["openingHours"] != []
            ):
                address = loc["address"]
                street = address["streetAddress"]
                pcode = address["postalCode"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                phone = loc["telephone"]
                lat = loc["geo"]["latitude"]
                longt = loc["geo"]["longitude"]
                hourslist = loc["openingHours"]
                title = loc["name"]
                store = loc["branchCode"]
                if len(street) < 2:
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    address = soup.find("input", {"id": "restAddress"})["value"]
                    street, city, state, pcode = address.split(",")
                    store = soup.find("input", {"id": "restID"})["value"]
                    title = soup.find("h1").text
                    phone = soup.find("span", {"id": "restPhoneNumber1"}).text
                hours = ""
                for hr in hourslist:
                    day = hr.split(" ", 1)[0]
                    start = hr.split(" ", 1)[1].split("-")[0]
                    end = hr.split(" ", 1)[1].split("-")[1]
                    check = (int)(end.split(":", 1)[0])
                    if check > 12:
                        endtime = check - 12
                    hours = (
                        hours
                        + day
                        + " "
                        + start
                        + " AM - "
                        + str(endtime)
                        + ":"
                        + end.split(":", 1)[1]
                        + " PM "
                    )
                hours = (
                    hours.replace("Mo", "Monday")
                    .replace("Tu", "Tuesday")
                    .replace("Th", "Thursday")
                    .replace("We", "Wednesday")
                    .replace("Fr", "Friday")
                    .replace("Sa", "Saturday")
                    .replace("Su", "Sunday")
                )

            else:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                address = soup.find("input", {"id": "restAddress"})["value"]

                street, city, state, pcode = address.split(",")
                try:
                    lat, longt = soup.find("input", {"id": "restLatLong"})[
                        "value"
                    ].split(",")
                except:
                    continue
                store = soup.find("input", {"id": "restID"})["value"]
                title = soup.find("h1").text
                phone = soup.find("span", {"id": "restPhoneNumber1"}).text
                hourlist = soup.find("div", {"class": "week-schedule"}).findAll(
                    "ul", {"class": "top-bar"}
                )
                hours = ""
                for hr in hourlist:
                    try:
                        nowhr = (
                            hr.find("li", {"class": "weekday"}).text
                            + " "
                            + hr.find("li", {"class": "rolling-hours-start"}).text
                            + " "
                        )
                    except:
                        nowhr = (
                            hr.find("li", {"class": "weekday-active"}).text
                            + " "
                            + hr.find("li", {"class": "rolling-hours-start"}).text
                            + " "
                        )

                    nowhr = (
                        nowhr.replace("Tue Nov 10 ", "")
                        .replace(":00 EST 2020", "")
                        .replace("\n", " ")
                    )
                    hours = hours + nowhr

            if store in storelist:
                continue
            storelist.append(store)
            data.append(
                [
                    "https://www.seasons52.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours.replace("\xa0", "").strip(),
                ]
            )
            p += 1

    return data


def scrape():
    data = fetch_data()
    write_output(data)
    driver.quit()


scrape()
