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
        for row in data:
            writer.writerow(row)


def fetch_data():
    p = 0
    data = []
    url = "https://www.homewatchcaregivers.com/locations/?CallAjax=GetLocations"
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:
        store = loc["FranchiseLocationID"]
        title = loc["FranchiseLocationName"]
        street = loc["Address1"] + " " + loc["Address2"]
        city = loc["City"]
        state = loc["State"]
        pcode = loc["ZipCode"]
        phone = loc["Phone"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        ccode = "US"
        if "CAN" in loc["Country"]:
            ccode = "CA"
        try:
            link = "https://www.homewatchcaregivers.com" + loc["Path"]
        except:
            link = loc["ExternalDomain"]
        r = session.get(link, headers=headers, verify=False)
        try:
            hours = r.text.split("24-hour-care", 1)[1].split("/")[0]
            hours = "24 Hours"
        except:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.homewatchcaregivers.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
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
