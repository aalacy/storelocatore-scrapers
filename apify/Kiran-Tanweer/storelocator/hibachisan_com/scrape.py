from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("hibachisan_com")

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
    i = 0
    pattern = re.compile(r"\s\s+")
    url_list = []
    coord_list = []
    url = "http://www.hibachisan.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    selectlist = soup.find("select", {"id": "ctl00_ContentPlaceHolder1_ddlState"})
    statelist = selectlist.find_all("option")
    statecode = [o.get("value") for o in statelist]

    # We have the state code list
    if statecode[0] == "-- SELECT --":
        statecode.pop(0)
    # for each state code, request!
    for element in statecode:
        url = "http://www.hibachisan.com/locations/locatorresults.aspx?state=" + element
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        maindiv = soup.find("div", {"id": "maincontenttext"})
        info = maindiv.find_all("span")
        spanid = [o.get("id") for o in info]
        if spanid[0] != "ctl00_ContentPlaceHolder1_lblNoStoresFound":
            url_list.append(url)
    nextpage = ""
    for url in url_list:
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        secondpage = soup.find("a", {"id": "ctl00_ContentPlaceHolder1_btnNext0"})
        if secondpage is not None:
            nextpage = secondpage.get("href")
            nextpage = "http://www.hibachisan.com" + nextpage
            url_list.append(nextpage)
    for url in url_list:
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find(
            "table", {"id": "ctl00_ContentPlaceHolder1_dlGetStoresByState"}
        )
        rowlist = table.findAll("table")
        for ele in rowlist:
            col = ele.findAll("td")[2]
            drive = col.find("a")
            if drive is not None:
                drive = drive["href"]
                coord_list.append(drive)
                coord_list.append(drive)

    for url in url_list:
        # print(url)
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find(
            "table", {"id": "ctl00_ContentPlaceHolder1_dlGetStoresByState"}
        )
        rowlist = table.findAll("table")

        for k in range(0, len(rowlist), 2):
            content = rowlist[k].text
            hours = rowlist[k + 1].text
            if "Directions" in content:
                content = content.split("Directions", 1)[0]
            content = re.sub(pattern, "\n", content)
            content = list(content.split("\n"))
            title = content[1]
            street = content[2]
            city = content[3]
            city = city.rstrip(",")
            state = content[4]
            zipcode = content[5]
            phone = content[6]
            phone = phone.lstrip("Phone: ")
            coords = coord_list[i]
            coord = coords.split("cp=")[1]
            coord = coord.split("&")[0]
            lat, longt = coord.split("~")
            i = i + 2
            if len(phone) == 0:
                phone = "<MISSING>"
            cleanr = re.compile(r"<[^>]+>")
            pattern = re.compile(r"\s\s+")
            hours = re.sub(cleanr, "\n", hours)
            hours = re.sub(pattern, "\n", hours)
            hours = hours.splitlines()
            week = hours[1]
            start_time = hours[2]
            end_time = hours[3]
            if start_time.find("AM") != -1:
                start_time = start_time.replace("AM", "AM-")
            if start_time.find("PM") != -1:
                start_time = start_time.replace("PM", "PM-")
            if start_time.find("CLOSE") != -1:
                start_time = start_time.replace("CLOSE", "CLOSE-")
            if end_time.find("AM") != -1:
                end_time = end_time.replace("AM", "AM ")
            if end_time.find("PM") != -1:
                end_time = end_time.replace("PM", "PM ")
            if end_time.find("CLOSE") != -1:
                end_time = end_time.replace("CLOSE", "CLOSE ")
            if week.find("day") != -1:
                week = week.replace("day", "day ")
            week = week.split(" ")
            week.remove("")
            split_start = []
            split_end = []
            # start_time = start_time.split('M ')
            if "CLOSE" not in start_time:
                for index in range(0, len(start_time), 9):
                    split_start.append(start_time[index: index + 9])
            else:
                for index in range(0, len(start_time), 6):
                    split_start.append(start_time[index: index + 6])
            if "CLOSE" not in end_time:
                for index in range(0, len(end_time), 8):
                    split_end.append(end_time[index: index + 8])
            else:
                for index in range(0, len(end_time), 6):
                    split_end.append(end_time[index: index + 6])
            schedule = ""
            time = []
            for a, b, c in zip(week, split_start, split_end):
                time = a + " " + b + c
                schedule = schedule + time
            data.append(
                [
                    "https://www.wienerschnitzel.com/",
                    url,
                    title,
                    street,
                    city,
                    state,
                    zipcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    schedule,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
