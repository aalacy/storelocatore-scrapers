from bs4 import BeautifulSoup
import csv
import json


from sgselenium import SgSelenium

driver = SgSelenium().chrome()


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
    p = 0
    data = []
    url = "https://www.110grill.com/locations"
    driver.get(url)
    divlist = driver.page_source.split(',"fullAddress":')[1:]
    linklist = []
    for div in divlist:
        div = div.split(',"openingRanges"', 1)[0]
        div = '{"fullAddress":' + div + "}"
        div = json.loads(div)
        title = div["name"]
        street = div["streetAddress"]
        city = title.split(",", 1)[0]
        state = div["state"]
        link = "https://www.110grill.com/" + div["slug"]
        lat = div["lat"]
        longt = div["lng"]
        hourlist = div["schemaHours"]
        hours = ""

        try:
            phone = div["phone"]
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            for hr in hourlist:
                temp = (int)(hr.split("-", 1)[1].split(":", 1)[0])
                if temp > 12:
                    temp = temp - 12
                hours = (
                    hours
                    + hr.split("-", 1)[0]
                    + " am - "
                    + str(temp)
                    + ":"
                    + hr.split("-", 1)[1].split(":", 1)[1]
                    + " pm "
                )
        except:
            hours = "Temporarily Closed"
            phone = "<MISSING>"
        pcode = div["postalCode"]
        if link in linklist:
            continue
        linklist.append(link)

        data.append(
            [
                "https://www.110grill.com/",
                link,
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
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
