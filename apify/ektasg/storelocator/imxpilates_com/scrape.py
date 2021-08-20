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
    url = "https://imxpilates.com/studios.php"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "et_pb_section_1_tb_body"}).select(
        'a:contains("IM=X®")'
    )
    p = 0
    for div in divlist:
        link = div["href"]
        if "#" in link or "http" in link:
            continue
        link = "https://www.imxpilates.com" + link
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "et_pb_column_inner_0_tb_body"})
        content = re.sub(cleanr, "\n", str(content)).strip()
        content = re.sub(pattern, "\n", content).strip().splitlines()
        title = content[0]
        phone = content[-1]
        try:
            city, state = content[-2].split(", ")
            street = " ".join(content[1 : len(content) - 2])
            state, pcode = state.lstrip().replace(", ", "").split(" ", 1)
        except:
            try:
                street = "14463 N. Dale Mabry Highway"
                city, state = content[-2].split(", Tampa", 1)[0].split(", ")
            except:
                phone = street = pcode = "<MISSING>"
                city = "Middle Village"
                state = "NY"
        try:
            state, pcode = state.strip().split(" ", 1)
        except:
            pass
        try:
            lat = r.text.split('"map_start_lat":"', 1)[1].split('"', 1)[0]
            longt = r.text.split('"map_start_lng":"', 1)[1].split('"', 1)[0]
        except:
            continue
        store = r.text.split("data-map-id='", 1)[1].split("'", 1)[0]
        data.append(
            [
                "https://www.imxpilates.com/",
                link,
                title,
                street.lstrip().replace(",", "").replace("-", "").replace("&amp;", "&"),
                city.lstrip().replace(",", ""),
                state.lstrip().replace(",", ""),
                pcode.lstrip().replace(",", ""),
                "US",
                store,
                phone.strip(),
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
