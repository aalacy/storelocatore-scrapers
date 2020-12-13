from bs4 import BeautifulSoup
import csv
import usaddress


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
    p = 0
    data = []
    url = "https://uptownjungle.com/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("LEARN MORE")')
    for link in linklist:
        link = link["href"]
        if "#" in link:
            continue
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = (
            soup.find("h1")
            .text.replace("\n", " ")
            .replace("\t", "")
            .replace("We Are Open!", "")
            .strip()
        )
        address = soup.find("div", {"class": "address"}).text
        longt, lat = (
            soup.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!3m", 1)[0]
            .split("!3d", 1)
        )
        num = link.split("//", 1)[1].split(".", 1)[0]
        num = num.replace("las", "las-")
        phone = "<MISSING>"
        phonelist = soup.find("div", {"id": "number"}).findAll("p")
        for ph in phonelist:
            if num in ph["id"]:
                phone = ph.text.strip()
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")
        hours = "Sun - Thurs 10am-6pm Fri-Sat 10am-8pm"
        try:
            lat = lat.split("!2m", 1)[0]
        except:
            pass
        data.append(
            [
                "https://uptownjungle.com/",
                link,
                title,
                street.replace("\n", ""),
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
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
