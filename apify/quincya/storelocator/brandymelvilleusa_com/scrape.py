import csv
import re
import time

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgselenium import SgChrome


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://us.brandymelville.com/apps/store-locator/all"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    time.sleep(10)

    base = BeautifulSoup(driver.page_source, "lxml")

    session = SgRequests()

    data = []

    items = base.find_all(class_="item thumbnail")

    for i in items:
        link = (
            "https://us.brandymelville.com" + i.find(class_="linkdetailstore")["href"]
        )

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        item = base.find(class_="store_detail col-md-4 col-md-pull-8")

        locator_domain = "brandymelville.com"

        try:
            location_name = base.h1.text.strip()
            got_page = True
        except:
            got_page = False

        if got_page:
            raw_address = (
                item.find(class_="entry-item")
                .text.strip()
                .replace(", United States", "")
            )
            if raw_address[-1:] == ",":
                raw_address = raw_address[:-1]

            raw_address = raw_address.split(",")
            street_address = (
                " ".join(raw_address[:-3])
                .strip()
                .split("Washington")[0]
                .split("Columbus")[0]
                .strip()
            )
            street_address = (re.sub(" +", " ", street_address)).strip()
            city = raw_address[-3].strip()
            state = raw_address[-2].strip()
            zip_code = raw_address[-1].strip()
            try:
                phone = item.a.text.strip()
            except:
                phone = "<MISSING>"
            hours_of_operation = " ".join(list(item.table.stripped_strings))
            geo = re.findall(
                r"lat:[0-9]{2}\.[0-9]+,lng:-[0-9]{2,3}\.[0-9]+", str(base)
            )[0].split(",")
            latitude = geo[0].split(":")[-1]
            longitude = geo[1].split(":")[-1]
        else:
            location_name = i.label.text.strip()
            raw_address = i.find(class_="address").text.split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zip_code = raw_address[3].strip()
            phone = i.find(class_="phone-no").text.strip()
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            link = base_link

        country_code = "US"
        store_number = i.find(class_="inner-item")["id"].split("_")[-1]
        location_type = "<MISSING>"

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
