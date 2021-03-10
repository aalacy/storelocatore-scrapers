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
    titlelist = []
    data = []
    url = "https://locations.outback.com/index.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("section", {"class": "StateList"}).findAll(
        "a", {"class": "Directory-listLink"}
    )
    p = 0
    for stnow in statelist:
        check1 = 0
        stlink = "https://locations.outback.com/" + stnow["href"]
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
                citylink = "https://locations.outback.com/" + citynow["href"]
                r = session.get(citylink, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    branchlist = soup.find(
                        "ul", {"class": "Directory-listTeasers"}
                    ).findAll("a", {"class": "Teaser-titleLink"})
                except:
                    branchlist = []
                    branchlist.append(citylink)
                    check2 = 1
            else:
                branchlist = []
                branchlist.append(citylink)
                check2 = 1
            for branch in branchlist:
                if check2 == 0:
                    branch = "https://locations.outback.com/" + branch["href"]
                    branch = branch.replace("../", "")
                    if branch in titlelist:
                        continue
                    titlelist.append(branch)
                    r = session.get(branch, headers=headers, verify=False)
                    soup = BeautifulSoup(r.text, "html.parser")
                store = r.text.split('"storeId":"', 1)[1].split('"', 1)[0]
                lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0]
                longt = r.text.split('"longitude":', 1)[1].split("}", 1)[0]
                title = (
                    soup.find("h1", {"id": "location-name"})
                    .text.replace("\n", " ")
                    .strip()
                )
                street = soup.find("span", {"class": "c-address-street-1"}).text
                city = soup.find("span", {"class": "c-address-city"}).text
                try:
                    state = soup.find("abbr", {"class": "c-address-state"}).text
                except:
                    continue
                pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                phone = soup.find("div", {"id": "phone-main"}).text
                hours = soup.find("table", {"class": "c-hours-details"}).text.replace(
                    "PM", "PM "
                )
                try:
                    hours = hours.split("Week", 1)[1]
                except:
                    pass
                data.append(
                    [
                        "https://outback.com",
                        branch,
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
                        hours.replace("Day of the WeekHours", "")
                        .replace("day", "day ")
                        .replace("Hours", "")
                        .strip(),
                    ]
                )

                p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
