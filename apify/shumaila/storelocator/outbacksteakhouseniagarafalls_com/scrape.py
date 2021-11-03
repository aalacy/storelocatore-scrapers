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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "http://outbacksteakhouseniagarafalls.com/"
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.find(
        "div", {"class": "overlay-container container-location"}
    ).findAll("div", {"class": "content"})
    for repo in repo_list:
        longt, lat = (
            repo.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d", 1)
        )
        repo = re.sub(cleanr, "\n", str(repo))
        repo = re.sub(pattern, "\n", repo).strip().splitlines()
        title = repo[0]
        ct = repo[1]
        street, phone = ct.split("•")
        phone = phone.strip()
        title = "Outback Steakhouse " + title
        hours = repo[2] + " " + repo[3]
        if hours.find("closed") > -1:
            hours = "Currently Closed"
        data.append(
            [
                "http://outbacksteakhouseniagarafalls.com/",
                "http://outbacksteakhouseniagarafalls.com/",
                title,
                street,
                "Niagara Falls",
                "Ontario",
                "<MISSING>",
                "CA",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
