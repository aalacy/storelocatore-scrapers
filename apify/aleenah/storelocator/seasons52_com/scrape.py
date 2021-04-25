from bs4 import BeautifulSoup
import csv
import json

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,ms;q=0.8,ur;q=0.7,lb;q=0.6",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
}


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


def fetch_data():
    # Your scraper here
    data = []
    url = "https://www.seasons52.com/site-map"
    r = session.get(url, headers=headers)
    storelist = []
    soup = BeautifulSoup(r.text, "html.parser")

    divlist = soup.select("a[href*=locations]")
    p = 0

    for div in divlist:
        if p == 0:
            link = (
                "https://www.seasons52.com/locations/fl/sunrise/sunrise-sawgrass/4548"
            )
        else:
            link = "https://www.seasons52.com" + div["href"]

        if link.find("all-locations") == -1:
            r = session.get(link, headers=headers, verify=False)
            loc = (
                r.text.split('<script type="application/ld+json">', 1)[1]
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
                    soup = BeautifulSoup(r.text, "html.parser")
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
                soup = BeautifulSoup(r.text, "html.parser")
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


scrape()
