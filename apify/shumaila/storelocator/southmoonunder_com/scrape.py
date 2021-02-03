import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": "dcc1d99f5de74de19c807f6583eecec2",
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
    url = "https://www.southmoonunder.com/api/StoreLocator/Search"
    p = 0
    myobj = {"SearchText": "", "SearchRadius": "10000", "Latitude": "", "Longitude": ""}
    loclist = session.post(url, data=myobj, headers=headers, verify=False).json()[
        "Data"
    ]["Locations"]
    for loc in loclist:
        title = loc["LocationName"]
        store = loc["LocationID"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        street = loc["Address1"]
        try:
            hours = loc["Schedule"].replace("<br />", " ").replace("\t", " ").strip()
        except:
            hours = "<MISSING>"
        try:
            street = street + " " + str(loc["Address2"])
        except:
            pass
        if len(hours) < 3:
            hours = "<MISSING>"
        city = loc["City"]
        state = loc["State"]
        pcode = loc["PostalCode"]
        phone = str(loc["PrimaryPhone"])
        if len(phone) < 7:
            phone = "<MISSING>"
        link = "https://www.southmoonunder.com/store?LocationID=" + str(store)

        data.append(
            [
                "https://www.southmoonunder.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
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
