from bs4 import BeautifulSoup
import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cinebistro_com")


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
    # Your scraper here
    data = []
    url = "https://www.cmxcinemas.com/Location/GetCinemaLocations"
    webdata = session.get(url, headers=headers, verify=False)
    webdata = BeautifulSoup(webdata.text, "html.parser")
    statelist = webdata.find("select", {"id": "drpStateloc"}).findAll("option")
    for state in statelist:
        if state.text == "Select your state":
            continue
        loclist = session.get(
            "https://www.cmxcinemas.com/Locations/FilterLocations?state="
            + state.text
            + "&city=&searchText="
        )
        loclist = json.loads(loclist.text)
        loclist = loclist["listloc"]
        for loc in loclist:
            if loc["totalcities"] == "0":
                pass
            else:
                citylist = loc["city"]
                state = loc["state"]
                for city in citylist:
                    title = city["cinemaname"]
                    if title == "CMX Odyssey IMAX":
                        street = city["address"].split(",")[0]
                    else:
                        street = city["address"]
                    pcode = city["postalcode"]
                    cityn = city["locCity"]
                    link = (
                        "https://www.cmxcinemas.com/Locationdetail/" + city["slugname"]
                    )
                    r = session.get(link, headers=headers, verify=False)
                    try:
                        longt, lat = (
                            r.text.split("!2d", 1)[1].split("!2m", 1)[0].split("!3d")
                        )
                    except:
                        lat = "<MISSING>"
                        longt = "<MISSING>"
                    data.append(
                        [
                            "https://www.cmxcinemas.com",
                            link,
                            title,
                            street,
                            cityn,
                            state,
                            pcode,
                            "US",
                            "<MISSING>",
                            "<MISSING>",
                            "<MISSING>",
                            lat,
                            longt,
                            "<MISSING>",
                        ]
                    )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
