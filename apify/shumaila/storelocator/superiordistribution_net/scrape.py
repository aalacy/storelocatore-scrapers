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
    url = "https://superiordistribution.net/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("div", {"class": "locations"})
    for loc in data_list:
        title = loc.find("a").text
        page_url = url + loc.find("a").get("href")
        storenum = "<MISSING>"
        if len(page_url) < 1:
            page_url = "<MISSING>"
        else:
            storenum = page_url.split("BranchId=")[1].split("&")[0]
        det = str(loc).replace("<br/>", "")
        det = BeautifulSoup(det, "html.parser")
        det = det.findAll("strong")
        street = det[0].next_sibling.split("\n")[1].lstrip()
        city = det[0].next_sibling.split("\n")[2].split(", ")[0].replace(" ", "")
        state = det[0].next_sibling.split("\n")[2].split(", ")[1].split(" ")[0]
        zip = det[0].next_sibling.split("\n")[2].split(", ")[1].split(" ")[1]
        phone = loc.findAll("a")[1].get("href")
        phone = str(phone).replace("tel:", "")
        hours_of_operation = (
            det[3].text
            + det[3].next_sibling.rstrip()
            + " "
            + det[4].text.rstrip()
            + det[4].next_sibling.rstrip()
        )
        hours_of_operation = hours_of_operation.replace("\n", ",")

        data.append(
            [
                "https://superiordistribution.net/",
                page_url,
                title,
                street,
                city,
                state,
                zip,
                "US",
                storenum,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
