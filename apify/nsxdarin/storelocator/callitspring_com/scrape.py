import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "x-aldo-brand": "callitspring",
    "x-aldo-region": "us",
}
headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "x-aldo-brand": "callitspring",
    "x-aldo-region": "ca",
}

logger = SgLogSetup().get_logger("callitspring_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    for x in range(3000, 4000):
        url = "https://www.callitspring.com/api/stores/" + str(x)
        r = session.get(url, headers=headers2)
        website = "callitspring.com"
        country = "CA"
        typ = "<MISSING>"
        loc = "https://www.callitspring.com/ca/en/store-locator/store/" + str(x)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        store = str(x)
        lat = ""
        lng = ""
        hours = ""
        logger.info("Pulling Store %s..." % str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"line1":"' in line:
                add = line.split('"line1":"')[1].split('"')[0]
                name = line.split('"mallName":"')[1].split('"')[0]
                phone = line.split('"phone":"')[1].split('"')[0].replace(".", "-")
                zc = line.split(',"postalCode":"')[1].split('"')[0]
                state = line.split('"isocodeShort":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(",")[0]
                lng = line.split('"longitude":')[1].split("}")[0]
                city = line.split('"town":"')[1].split('"')[0]
                days = (
                    line.split('"weekDayOpeningList":[')[1]
                    .split("]}")[0]
                    .split('"closingTime":')
                )
                for day in days:
                    if '"openingTime"' in day:
                        hrs = (
                            day.split('"weekDay":"')[1].split('"')[0]
                            + ": "
                            + day.split('"formattedHour":"')[2].split('"')[0]
                            + "-"
                            + day.split('"formattedHour":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                    if '"closed":true' in day:
                        hrs = day.split('"weekDay":"')[1].split('"')[0] + ": Closed"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if name != "":
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if "0" not in hours:
                hours = "Sun-Sat: Closed"
            if hours.count("Th:") == 2:
                hours = hours.replace("Th: Closed", "Fr: Closed")
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]
    for x in range(3320, 4000):
        url = "https://www.callitspring.com/api/stores/" + str(x)
        r = session.get(url, headers=headers)
        website = "callitspring.com"
        country = "US"
        typ = "<MISSING>"
        loc = "https://www.callitspring.com/us/en_US/store-locator/store/" + str(x)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        store = str(x)
        lat = ""
        lng = ""
        hours = ""
        logger.info("Pulling Store %s..." % str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"line1":"' in line:
                add = line.split('"line1":"')[1].split('"')[0]
                name = line.split('"mallName":"')[1].split('"')[0]
                phone = line.split('"phone":"')[1].split('"')[0].replace(".", "-")
                zc = line.split(',"postalCode":"')[1].split('"')[0]
                state = line.split('"isocodeShort":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(",")[0]
                lng = line.split('"longitude":')[1].split("}")[0]
                city = line.split('"town":"')[1].split('"')[0]
                days = (
                    line.split('"weekDayOpeningList":[')[1]
                    .split("]}")[0]
                    .split('"closingTime":')
                )
                for day in days:
                    if '"openingTime"' in day:
                        hrs = (
                            day.split('"weekDay":"')[1].split('"')[0]
                            + ": "
                            + day.split('"formattedHour":"')[2].split('"')[0]
                            + "-"
                            + day.split('"formattedHour":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                    if '"closed":true' in day:
                        hrs = day.split('"weekDay":"')[1].split('"')[0] + ": Closed"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if name != "":
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if "0" not in hours:
                hours = "Sun-Sat: Closed"
            if hours.count("Th:") == 2:
                hours = hours.replace("Th: Closed", "Fr: Closed")
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
