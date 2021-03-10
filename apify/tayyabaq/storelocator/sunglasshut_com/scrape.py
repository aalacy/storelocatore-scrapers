from bs4 import BeautifulSoup
import csv

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    data = []
    p = 0
    ccode = "US"
    urlist = ["https://stores.sunglasshut.com/us", "https://stores.sunglasshut.com/ca"]
    for url in urlist:
        if "/ca" in url:
            ccode = "CA"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("section", {"class": "StateList"}).findAll(
            "a", {"class": "Directory-listLink"}
        )

        for stnow in statelist:
            check1 = 0
            stlink = "https://stores.sunglasshut.com/" + stnow["href"]
            r = session.get(stlink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                citylist = soup.find("section", {"class": "CityList"}).findAll(
                    "a", {"class": "Directory-listLink"}
                )
            except:
                citylist = []
                citylist.append(stlink)
                check1 = 1
            for citynow in citylist:
                check2 = 0
                if check1 == 0:
                    citylink = "https://stores.sunglasshut.com/" + citynow["href"]
                    citylink = citylink.replace("../", "")

                    r = session.get(citylink, headers=headers, verify=False)
                    soup = BeautifulSoup(r.text, "html.parser")
                else:
                    branchlist = []
                    branchlist.append(citynow)
                    check2 = 1
                try:
                    branchlist = soup.find(
                        "ul", {"class": "Directory-listTeasers"}
                    ).findAll("a", {"class": "Teaser-titleLink"})

                    check2 = 0
                except:

                    branchlist = []
                    branchlist.append(citylink)
                    check2 = 1
                for branch in branchlist:
                    if check2 == 0:
                        branch = "https://stores.sunglasshut.com/" + branch["href"]
                        branch = branch.replace("../", "")

                        r = session.get(branch, headers=headers, verify=False)
                        soup = BeautifulSoup(r.text, "html.parser")
                        branch = r.url
                    store = (
                        soup.select_one("a[href*=storeId]")["href"]
                        .split("storeId=", 1)[1]
                        .split("&", 1)[0]
                    )
                    lat = soup.find("meta", {"itemprop": "latitude"})["content"]
                    longt = soup.find("meta", {"itemprop": "longitude"})["content"]
                    title = (
                        soup.find("h1", {"class": "Core-name"})
                        .text.replace("\n", " ")
                        .strip()
                    )
                    street = soup.find("span", {"class": "c-address-street-1"}).text
                    try:
                        street = (
                            street
                            + " "
                            + soup.find("span", {"class": "c-address-street-2"}).text
                        )
                    except:
                        pass
                    city = soup.find("span", {"class": "c-address-city"}).text
                    try:
                        state = soup.find("abbr", {"class": "c-address-state"}).text
                    except:
                        continue
                    pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                    phone = soup.find("div", {"id": "phone-main"}).text
                    try:
                        hours = (
                            soup.find("table", {"class": "c-hours-details"})
                            .text.replace("PM", "PM ")
                            .replace("day", "day ")
                        )
                        try:
                            hours = hours.split("Week", 1)[1]
                        except:
                            pass
                        try:
                            hours = hours.split("Hours", 1)[1]
                        except:
                            pass
                    except:
                        hours = "Temporarily Closed"
                    branch = r.url
                    data.append(
                        [
                            "https://sunglasshut.com/",
                            branch,
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

                    p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
