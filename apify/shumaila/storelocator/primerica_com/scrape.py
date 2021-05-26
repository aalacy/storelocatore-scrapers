from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests

session1 = SgRequests()
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
    linklist = []
    data = []
    p = 0
    url = "http://www.primerica.com/public/locations.html"
    page = session1.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    maidiv = soup.find("main")
    mainsection = maidiv.findAll("section", {"class": "content locList"})
    sec = 0
    while sec < 2:
        if sec == 0:
            ccode = "US"
        if sec == 1:
            ccode = "CA"
        rep_list = mainsection[sec].findAll("a")
        cleanr = re.compile("<.*?>")
        pattern = re.compile(r"\s\s+")
        for rep in rep_list:
            link = "http://www.primerica.com/public/" + rep["href"]

            if True:
                session = SgRequests()
                page1 = session.get(link, headers=headers)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                maindiv = soup1.find("main")
                xip_list = maindiv.findAll("a")

                for xip in xip_list:
                    if True:
                        pcode = xip.text

                        statelink = "http://www.primerica.com" + xip["href"]
                        page2 = session1.get(statelink, headers=headers, verify=False)
                        soup2 = BeautifulSoup(page2.text, "html.parser")
                        mainul = soup2.find("ul", {"class": "agent-list"})
                        li_list = mainul.findAll("li")
                        for m in range(0, len(li_list)):
                            if True:
                                address = ""
                                alink = li_list[m].find("a")

                                title = alink.text
                                alink = alink["href"] + "&origin=customStandard"
                                if alink in linklist:
                                    continue
                                linklist.append(alink)

                                page3 = session.get(
                                    alink, headers=headers, verify=False
                                )

                                soup3 = BeautifulSoup(page3.text, "html.parser")
                                address = soup3.find(
                                    "div", {"class": "officeInfoDataWidth"}
                                )
                                cleanr = re.compile(r"<[^>]+>")
                                address = cleanr.sub(" ", str(address))
                                address = re.sub(pattern, "\n", address).lstrip()
                                address = address.splitlines()

                                city = ""
                                state = ""
                                i = 0
                                street = address[i]
                                i += 1
                                try:
                                    if address[i].find(",") == -1:
                                        street = street + " " + address[i]
                                        i += 1
                                    else:
                                        city, state = address[i].split(", ")
                                except:
                                    data.append(
                                        [
                                            "http://www.primerica.com/",
                                            alink,
                                            title,
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                        ]
                                    )

                                    p += 1
                                    continue
                                if address[i].find(",") > -1:
                                    city, state = address[i].split(", ")
                                i += 1
                                pcode = address[i]
                                if len(state) > 4:
                                    street = address[0] + " " + address[1]
                                    city, state = address[2].split(",", 1)
                                    state = state.lstrip()
                                    pcode = address[3]
                                phone = soup3.find(
                                    "div", {"class": "telephoneLabel"}
                                ).text
                                phone = phone.replace("Office: ", "")
                                phone = phone.replace("Mobile", "")
                                phone = phone.replace(":", "")
                                phone = phone.strip()
                                if len(phone) < 2:
                                    phone = "<MISSING>"
                                if len(street) < 2:
                                    street = "<MISSING>"
                                if len(city) < 2:
                                    city = "<MISSING>"
                                if len(state) < 2:
                                    state = "<MISSING>"
                                if len(pcode) < 2:
                                    pcode = "<MISSING>"
                                if len(phone) < 11:
                                    phone = "<MISSING>"
                                street = street.lstrip().replace(",", "")
                                city = city.lstrip().replace(",", "")
                                state = state.lstrip().replace(",", "")
                                pcode = pcode.lstrip().replace(",", "").rstrip()

                                if (
                                    pcode.find("-") == -1
                                    and sec == 0
                                    and pcode != "<MISSING>"
                                    and len(pcode) > 6
                                ):
                                    pcode = pcode[0:5] + "-" + pcode[5 : len(pcode)]
                                if state == "NF":
                                    state = "NL"
                                if state == "PQ":

                                    state = "QC"
                                if True:
                                    data.append(
                                        [
                                            "http://www.primerica.com/",
                                            alink,
                                            title,
                                            street,
                                            city,
                                            state,
                                            pcode.rstrip(),
                                            ccode,
                                            "<MISSING>",
                                            phone,
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                            "<MISSING>",
                                        ]
                                    )

                                    p += 1
        sec += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
