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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.fordsgarageusa.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup1 = BeautifulSoup(r.text, "html.parser")
    divlist = soup1.findAll("div", {"class": "service-content"})
    for div in divlist:
        flag = 0
        title = div.find("h4").text
        link = "https://www.fordsgarageusa.com" + div.find("a")["href"]
        try:
            hours = div.find("p", {"class": "hours-row"}).text
        except:
            hours = div.select_one('p:contains("Monday")').text
        if "OPENING SOON!" in hours:
            continue
        phone = div.select_one("a[href*=tel]").text
        plist = div.findAll("p")
        count = 0
        for adr in plist:
            if "phone" in adr.text.lower():
                break
            else:
                count = count + 1
        if "Phone" in plist[1].text:
            content = re.sub(cleanr, "\n", str(plist[0]))
            content = re.sub(pattern, "\n", str(content)).strip().splitlines()
            street = content[0]
            city, state = content[1].split(", ")
        else:
            if count == 2:
                street = plist[0].text
                try:
                    city, state = plist[1].text.split(", ")
                except:
                    street = plist[0].text + " " + plist[1].text
                    flag = 1
            elif count == 3:
                street = plist[0].text + " " + plist[1].text
                city, state = plist[2].text.split(", ")
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        if flag == 1:
            adr = soup.select_one("a[href*=map]").text
            city, state = adr.split(plist[1].text, 1)[1].split(", ", 1)
        try:
            maplink = soup.select_one("a[href*=map]")["href"]
            r = session.get(maplink, headers=headers, verify=False)
            lat, longt = r.url.split("@", 1)[1].split("data", 1)[0].split(",", 1)
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        state, pcode = state.strip().split(" ", 1)

        data.append(
            [
                "https://www.fordsgarageusa.com",
                link,
                title,
                street,
                city.replace("\n", "").strip(),
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours.replace("\n", " ").strip(),
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
