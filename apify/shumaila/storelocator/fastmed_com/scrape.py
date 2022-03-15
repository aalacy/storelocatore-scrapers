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
    p = 0
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.carespot.com/wp-admin/admin-ajax.php"
    myobj = {"action": "locations-get_map_locations"}
    loclist = session.post(url, data=myobj, headers=headers, verify=False).json()[
        "data"
    ]
    for loc in loclist:

        title = loc["title"]
        info = loc["info"].replace("\n", "")
        soup = BeautifulSoup(info, "html.parser")
        link = soup.find("a")["href"]
        address = soup.find("p", {"itemprop": "address"})
        address = re.sub(cleanr, "\n", str(address))
        address = re.sub(pattern, "\n", str(address)).strip().splitlines()
        street = address[0]
        city = address[1]
        state = address[-2]
        pcode = address[-1]
        if len(state) > 2:
            if "Suit" in city:
                street = street + " " + city
            city, state = pcode.split(", ", 1)
            state = re.sub(pattern, " ", state).strip()

            state, pcode = str(state).replace("\t", " ").strip().split(" ", 1)
        try:
            phone = soup.find("span", {"itemprop": "telephone"}).text
        except:
            phone = "<MISSING>"
        try:
            if "Coming Soon" in soup.find("h4").text:
                continue
        except:
            pass
        lat = loc["lat"]
        longt = loc["lng"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = soup.find("div", {"class": "hours"}).text
            hours = hours.split("Hours", 1)[1].replace("pm", "pm ")
        except:
            try:
                hours = soup.find("div", {"id": "hours"}).text
                hours = re.sub(pattern, " ", hours).strip()
                try:
                    hours = hours.split("Holiday", 1)[0]
                except:
                    pass
                try:
                    hours = hours.split("Urgent", 1)[1].split("hours", 1)[1]
                except:
                    pass
            except:
                hours = "<MISSING>"
        try:
            hours = hours.split("Family", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Sport", 1)[0]
        except:
            pass
        data.append(
            [
                "https://www.fastmed.com/",
                link,
                title.replace("&amp;", "&").replace("&#8211;", "-").strip(),
                street.replace("\xa0", " ").strip(),
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours.replace("\n", " ").replace("\xa0", " ").strip(),
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
