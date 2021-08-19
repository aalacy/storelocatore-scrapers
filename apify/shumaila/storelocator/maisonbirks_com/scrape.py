import csv
import json
from sgrequests import SgRequests


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    url = "https://www.maisonbirks.com/en/store/locator/ajaxlist/"
    province = {
        "Alberta": "AB",
        "British Columbia": "BC",
        "Manitoba": "MB",
        "New Brunswick": "NB",
        "Newfoundland and Labrador": "NL",
        "Northwest Territories": "NT",
        "Nova Scotia": "NS",
        "Nunavut": "NU",
        "Ontario": "ON",
        "Prince Edward Island": "PE",
        "Quebec": "QC",
        "Saskatchewan": "SK",
        "Yukon": "YT",
        "Florida": "FL",
        "Albama": "AL",
        "Alabama": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "District of Columbia": "DC",
    }

    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(":", 1)[1].split(',"is_last_page')[0]
    r = json.loads(r)
    for store in r:

        label = False
        try:
            if store["additional_attributes"]["type"]["label"] == "Store":
                label = True
            else:
                label = False
        except:
            pass
        if label and (store["country_id"] == "US" or store["country_id"] == "CA"):
            ltype = "<MISSING>"  # store['additional_attributes']['type']['label']
            storeid = "<MISSING>"
            title = store["name"]
            try:
                ccode = store["country_id"]
            except:
                ccode = "CA"
            city = store["city"]
            pcode = store["postcode"]
            state = store["region"]
            state = province[state]
            street = store["address"][0]
            street = street.split(city)[0].replace(",", "")
            link = store["additional_attributes"]["url_key"]
            lat = store["latitude"]
            longt = store["longitude"]
            phone = store["telephone"]
            hourd = store["opening_hours"]
            hourd = json.loads(hourd)
            if True:  # ltype.lower().find("store") > -1:
                hours = ""
                for hr in hourd:
                    opend = hr["open_formatted"]
                    closed = hr["close_formatted"]
                    if len(opend) < 2:
                        opend = "Closed"
                    else:
                        opend = opend + " - " + closed
                    hours = hours + hr["dayLabel"] + " : " + opend + " "
            else:
                hours = "<MISSING>"
            data.append(
                [
                    "https://www.maisonbirks.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    storeid,
                    phone,
                    ltype,
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
