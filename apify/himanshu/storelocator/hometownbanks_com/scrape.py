import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hometownbanks_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_url = "https://www.hometownbanks.com"
    r = session.get("https://www.hometownbanks.com/MCB/Map/Markers.js")

    json_data = r.text.split("locationData = ")[1].split("}]")[0] + "}]"
    json_data = json_data.replace("new google.maps", '"new google.maps').replace(
        '),"title"', ')","title"'
    )
    json_data = json.loads(json_data)
    lat_lng = {}
    casey_lat_lng = {}
    caseycount = 0

    for loc in json_data:
        lat = loc["position"].split("LatLng(")[1].split(",")[0].strip()
        lng = loc["position"].split("LatLng(")[1].split(",")[1].split(")")[0].strip()
        address = loc["address"]
        title = loc["title"].replace("&#39;", "'")

        add_details = address.split(",")

        state = add_details[-1].strip()
        city = add_details[-2].strip()
        street = add_details[-3]
        if title != "Casey's":
            lat_lng[title] = {
                "lat": lat,
                "lng": lng,
                "street": street,
                "city": city,
                "state": state,
            }
        else:
            casey_lat_lng["Casey's" + str(caseycount)] = {
                "lat": lat,
                "lng": lng,
                "street": street,
                "city": city,
                "state": state,
            }
            caseycount = caseycount + 1
    fin_lat = ""
    fin_lng = ""
    r = session.get("https://www.hometownbanks.com/Locations/All")
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("div", {"class": "row py-2"})
    count = 0
    for loc in data_list:
        hours_of_operation = ""
        details = loc.findAll("div", {"class": "col-12 col-md-3"})
        html_title = (
            loc.find("div", {"class": "col-12 col-md"}).find("p").find("strong").text
        )
        fin_title = html_title

        if html_title == "Casey's":
            html_title = "Casey's" + str(count)
            fin_title = "Casey's"

            count = count + 1
            fin_zip = loc.find("div", {"class": "col-12 col-md"}).find("p")
            fin_zip = str(fin_zip).replace("<br/>", "|")
            fin_zip = BeautifulSoup(fin_zip, "html.parser")
            fin_street = str(fin_zip).split("|")[1]
            fin_city = str(fin_zip).split("|")[2].split(", ")[0]
            fin_state = str(fin_zip).split("|")[2].split(", ")[1].split(" ")[0]
            fin_phone = ""
            if (len(str(fin_zip).split("|"))) > 3:
                fin_phone = (
                    str(fin_zip)
                    .split("|")[3]
                    .replace("ATM not owned or operated by Morton Community Bank", "")
                    .replace("</p>", "")
                )
            else:
                fin_phone = "<MISSING>"
            if fin_phone == "":
                fin_phone = "<MISSING>"
            fin_zip = (
                str(fin_zip)
                .split("|")[2]
                .split(", ")[1]
                .split(" ")[1]
                .replace("</p", "")
                .replace(">", "")
            )
            for key, value in casey_lat_lng.items():
                json_street = value["street"]
                if str(fin_street) in json_street:
                    fin_lat = value["lat"]
                    fin_lng = value["lng"]
            hours_of_operation = ""
            for det in details:
                if "Lobby Hours" in det.text:
                    det = str(det).replace("<br/>", " ")
                    det = BeautifulSoup(det, "html.parser")
                    hoo = det.findAll("p")
                    for p in hoo:
                        hours_of_operation = hours_of_operation + p.text + " "
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
        else:
            fin_lat = lat_lng[html_title]["lat"]
            fin_lng = lat_lng[html_title]["lng"]
            fin_zip = loc.find("div", {"class": "col-12 col-md"}).find("p")
            fin_zip = str(fin_zip).replace("<br/>", "|")

            fin_zip = BeautifulSoup(fin_zip, "html.parser")
            fin_phone = ""
            if (len(str(fin_zip).split("|"))) > 3:
                fin_phone = (
                    str(fin_zip)
                    .split("|")[3]
                    .replace("ATM not owned or operated by Morton Community Bank", "")
                    .replace("</p>", "")
                )
            else:
                fin_phone = "<MISSING>"
            if fin_phone == "":
                fin_phone = "<MISSING>"
            fin_street = str(fin_zip).split("|")[1]
            fin_city = str(fin_zip).split("|")[2].split(", ")[0]
            fin_state = str(fin_zip).split("|")[2].split(", ")[1].split(" ")[0]

            fin_zip = (
                str(fin_zip)
                .split("|")[2]
                .split(", ")[1]
                .split(" ")[1]
                .replace("</p", "")
                .replace(">", "")
            )
            for det in details:
                if "Lobby Hours" in det.text:
                    det = str(det).replace("<br/>", " ")
                    det = BeautifulSoup(det, "html.parser")
                    hoo = det.findAll("p")
                    for p in hoo:
                        hours_of_operation = hours_of_operation + p.text + " "
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
        data.append(
            [
                base_url,
                "https://www.hometownbanks.com/Locations/All",
                fin_title,
                fin_street,
                fin_city,
                fin_state,
                fin_zip,
                "US",
                "<MISSING>",
                fin_phone,
                "<MISSING>",
                fin_lat,
                fin_lng,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
