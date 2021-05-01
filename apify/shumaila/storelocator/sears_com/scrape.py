from bs4 import BeautifulSoup
import csv
import re
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
    links = []
    pattern = re.compile(r"\s\s+")
    url = "https://www.sears.com/stores.html"
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find("ul", {"class": "shc-search-by-state__list"})
    statelist = mainul.findAll("a")
    for state in statelist:
        if state["href"].find("404") == -1:
            statelink = "https://www.sears.com" + state["href"]
            state1 = state.text
            flag1 = True
            while flag1:
                try:
                    page1 = session.get(statelink, headers=headers, verify=False)
                    soup1 = BeautifulSoup(page1.text, "html.parser")
                    maindiv = soup1.find("div", {"class": "shc-quick-links"})
                    linklist = soup1.findAll(
                        "li", {"class": "shc-quick-links--store-details__list--stores"}
                    )
                    for blinks in linklist:
                        link = blinks.find("a")["href"]
                        state1 = blinks.find("a").text.split(",")[1].split("\n", 1)[0]
                        if (
                            link.find("http") == -1
                            and blinks.text.find("Sears Store") > -1
                        ):
                            link = "https://www.sears.com" + link
                            flag = True
                            while flag:
                                try:
                                    page2 = session.get(
                                        link, headers=headers, verify=False
                                    )
                                    time.sleep(2)

                                    if page2.url.find("closed") > -1:
                                        break
                                    else:

                                        soup2 = BeautifulSoup(page2.text, "html.parser")

                                        try:
                                            title = (
                                                soup2.find(
                                                    "h1",
                                                    {"class": "shc-save-store__title"},
                                                )["data-store-title"]
                                                + soup2.find(
                                                    "h1",
                                                    {"class": "shc-save-store__title"},
                                                )["data-unit-number"]
                                            )
                                        except:

                                            title = soup2.find(
                                                "small", {"itemprop": "name"}
                                            ).text
                                        title = title.replace("\n", " ").replace(
                                            "000", " # "
                                        )
                                        title = re.sub(pattern, " ", title)
                                        start = title.find("#")
                                        if start != -1:
                                            store = title.split("#", 1)[1].lstrip()
                                        else:
                                            store = "<MISSING>"
                                        mainp = soup2.find(
                                            "p",
                                            {
                                                "class": "shc-store-location__details--address"
                                            },
                                        ).findAll("span")
                                        try:
                                            street = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[0]
                                                .text
                                            )
                                            street = street.lstrip()
                                        except Exception as e:
                                            street = "<MISSING>"
                                        try:
                                            city = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[1]
                                                .text.split(", ")[0]
                                            )
                                            city = city.lstrip()
                                        except:
                                            city = "<MISSING>"
                                        pcode = "<MISSING>"
                                        try:
                                            pcode = (
                                                soup2.find(
                                                    "p",
                                                    {
                                                        "class": "shc-store-location__details--address"
                                                    },
                                                )
                                                .findAll("span")[1]
                                                .text.split(", ")[1]
                                            )
                                        except:
                                            state = "<MISSING>"
                                        try:
                                            phone = soup2.find(
                                                "strong",
                                                {
                                                    "class": "shc-store-location__details--tel"
                                                },
                                            ).text
                                        except:
                                            phone = "<MISSING>"
                                        try:
                                            hourd = soup2.find(
                                                "div",
                                                {"class": "shc-store-hours__details"},
                                            ).findAll("li")
                                            hours = ""
                                            for hour in hourd:

                                                hours = hours + hour.text + " "
                                                hours = re.sub(pattern, " ", hours)
                                        except:
                                            hours = "<MISSING>"
                                        try:
                                            coord = soup2.find(
                                                "div", {"class": "shc-store-location"}
                                            )
                                            lat = coord["data-latitude"]
                                            longt = coord["data-longitude"]
                                        except:
                                            lat = "<MISSING>"
                                            longt = "<MISSING>"
                                        hours = hours.replace("\n", " ")
                                        hours = hours.strip()
                                        title = title.lstrip()
                                        title = title.encode("ascii", "ignore").decode(
                                            "ascii"
                                        )
                                        title = title.replace("Sears", "Sears ")
                                        title = title.replace("  ", " ")
                                        flag = True
                                        for i in range(0, len(data)):

                                            if (
                                                link == data[i][1]
                                                and title == data[i][2]
                                            ):

                                                flag = False
                                                break
                                        if (
                                            flag
                                            and title.lower().find(
                                                "find your next closest Store"
                                            )
                                            == -1
                                        ):
                                            data.append(
                                                [
                                                    "https://www.sears.com/",
                                                    link,
                                                    title,
                                                    street,
                                                    city,
                                                    state1,
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

                                            flag = False
                                except Exception as e:

                                    pass
                    flag1 = False
                except Exception as e:

                    pass
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
