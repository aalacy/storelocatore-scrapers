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
    url = "https://www.pfchangs.com/locations/us.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    statelist = soup.find("section", {"class": "StateList"}).findAll(
        "a", {"class": "Directory-listLink"}
    )
    p = 0
    for stnow in statelist:
        check1 = 0
        stlink = "https://www.pfchangs.com/locations/" + stnow["href"]

        r = session.get(stlink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        citylist = []
        try:
            citylist = soup.find("section", {"class": "CityList"}).findAll(
                "a", {"class": "Directory-listLink"}
            )
        except:
            citylist = []
            citylist.append(stlink)
            check1 = 1
        if len(citylist) == 1:
            citylist = []
            citylist.append(stlink)
            check1 = 1
        for citynow in citylist:
            check2 = 0
            if check1 == 0:
                citylink = citynow["href"].replace(
                    "../", "https://www.pfchangs.com/locations/"
                )
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
                if len(branchlist) == 0:
                    branchlist = []
                    branchlist.append(citylink)
                    check2 = 1
            else:
                branchlist = []
                branchlist.append(citynow)
                check2 = 1
            for branch in branchlist:
                if check2 == 0:
                    branch = branch["href"].replace(
                        "../../../../", "https://www.pfchangs.com/locations/"
                    )
                    branch = branch.replace(
                        "../../", "https://www.pfchangs.com/locations/"
                    )

                    r = session.get(branch, headers=headers, verify=False)
                    soup = BeautifulSoup(r.text, "html.parser")
                try:
                    title = soup.find("h1").find("span", {"class": "LocationName"}).text
                except:
                    pass
                link = branch.replace("../", "")
                street = soup.find("meta", {"itemprop": "streetAddress"})["content"]
                city = soup.find("meta", {"itemprop": "addressLocality"})["content"]
                lat = soup.find("meta", {"itemprop": "latitude"})["content"]
                longt = soup.find("meta", {"itemprop": "longitude"})["content"]
                pcode = soup.find("span", {"itemprop": "postalCode"}).text
                state = soup.find("abbr", {"itemprop": "addressRegion"}).text
                phone = soup.find("div", {"itemprop": "telephone"}).text
                store = link.split("/")[-1].split("-", 1)[0]
                hours = soup.find("table", {"class": "c-hours-details"}).text
                hours = hours.replace("PM", "PM ").replace(street, "")
                hours = hours.replace("Day of the WeekHours", "")
                hours = hours.replace("11", " 11")
                hours = hours.replace("Closed", " Closed ")
                store = store.replace(".html", "")
                if link in titlelist:
                    continue
                titlelist.append(link)
                data.append(
                    [
                        "https://www.pfchangs.com/",
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
                        hours,
                    ]
                )

                p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
