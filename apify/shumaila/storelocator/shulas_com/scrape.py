from bs4 import BeautifulSoup
import csv
import re
import json

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
    url = "https://shulassteakhouse.com/#locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "shula-menu__location"})
    p = 0
    flag = 0
    for div in divlist:

        if True:
            link = div.find("a")["href"]

            if link != "https://shulasbarandgrill.com/" and link.find("location") == -1:
                link = link.replace(".com/", ".com/location-")
            r = session.get(link, headers=headers, verify=False)
            if link == "https://shulasbarandgrill.com/" and flag == 1:
                continue
            if link == "https://shulasbarandgrill.com/" and flag == 0:
                flag = 1
                soup = BeautifulSoup(r.text, "html.parser")
                titlelist = soup.findAll("div", {"class": "location"})
                addresslist = soup.findAll("div", {"class": "location-info"})
                for i in range(0, len(titlelist)):
                    title = titlelist[i].text
                    address = addresslist[i].text.splitlines()
                    city, state = address[-1].split(", ")
                    state, pcode = state.lstrip().split(" ", 1)
                    street = " ".join(address[0 : len(address) - 1])

                    data.append(
                        [
                            "https://shulas.com/",
                            link,
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            "US",
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
            try:
                title = div.find("a").text
                jslink = (
                    "https://knowledgetags.yextpages.net"
                    + r.text.split("https://knowledgetags.yextpages.net", 1)[1].split(
                        '"', 1
                    )[0]
                )
                r = session.get(jslink, headers=headers, verify=False)
                address = r.text.split('"address":{', 1)[1].split("}", 1)[0]
                address = "{" + address + "}"
                address = json.loads(address)
                street = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                pcode = address["postalCode"]
                try:
                    phone = (
                        r.text.split('"telephone":"', 1)[1]
                        .split('"')[0]
                        .replace("+1", "")
                    )
                except:
                    phone = "<MISSING>"
                hours = ""
                try:
                    hourlist = r.text.split('"openingHoursSpecification":[', 1)[
                        1
                    ].split("],", 1)[0]
                    hourlist = "[" + hourlist + "]"
                    hourlist = json.loads(hourlist)

                    for hour in hourlist:
                        starttime = hour["opens"]
                        start = (int)(starttime.split(":")[0])
                        if start > 12:
                            start = start - 12
                        endtime = hour["closes"]
                        end = (int)(endtime.split(":")[0])
                        if end > 12:
                            end = end - 12
                        hours = (
                            hours
                            + hour["dayOfWeek"]
                            + " "
                            + str(start)
                            + ":"
                            + starttime.split(":")[1]
                            + " AM - "
                            + str(end)
                            + ":"
                            + endtime.split(":")[1]
                            + " PM  "
                        )
                except:
                    hours = "<MISSING>"
                try:
                    lat = r.text.split('"latitude":', 1)[1].split(",")[0]
                except:
                    lat = "<MISSING>"
                try:
                    longt = r.text.split('"longitude":', 1)[1].split("}")[0]
                except:
                    longt = "<MISSING>"
                data.append(
                    [
                        "https://shulas.com/",
                        link,
                        title,
                        street,
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
            except:
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    content = soup.find(
                        "div", {"class": "shula-block-split-content-body"}
                    )
                    content = re.sub(cleanr, "\n", str(content)).strip()
                    content = (
                        re.sub(pattern, "\n", content)
                        .replace(" &amp; ", " & ")
                        .splitlines()
                    )
                    m = 0
                    street = content[m]
                    try:
                        city, state = content[m + 1].split(", ", 1)
                    except:
                        m = 2
                        street = content[m]
                        city, state = content[m + 1].split(", ", 1)
                    state, pcode = state.lstrip().split(" ", 1)
                    phone = content[m + 2].replace("Phone", "").replace(":", "")
                    hours = " ".join(content[m + 3 :])
                    if hours.find("temporarily closed") > -1:
                        hours = "Temporarily Closed"
                    else:
                        if hours.find("Dine") > -1:
                            hours = " ".join(content[m + 4 :])
                    phone = phone.replace("Tel ", "")
                    longt, lat = (
                        soup.find("div", {"class": "embed-container"})
                        .find("iframe")["src"]
                        .split("!2d", 1)[1]
                        .split("!2m", 1)[0]
                        .split("!3d")
                    )
                    try:
                        hours = hours.split(" Email Us", 1)[0]
                    except:
                        pass
                    hours = hours.replace("Hours", "")
                    data.append(
                        [
                            "https://shulas.com/",
                            link,
                            title,
                            street,
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
                except:
                    try:
                        content = soup.find(
                            "div", {"class": "shula-block-split-content-body"}
                        ).findAll("p")
                    except:
                        continue
                    for i in range(1, len(content)):
                        det = content[i].text.splitlines()
                        title = det[0]
                        street = det[1]
                        try:
                            city, state = det[2].split(", ")
                        except:
                            street = street + " " + det[2]
                            city, state = det[3].split(", ")
                        state, pcode = state.lstrip().split(" ", 1)

                        data.append(
                            [
                                "https://shulas.com/",
                                link,
                                title,
                                street,
                                city,
                                state,
                                pcode,
                                "US",
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>",
                            ]
                        )
                    p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
