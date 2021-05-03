import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "authority": "1-dot-rogers-store-finder.appspot.com",
    "path": "/searchChatrStoresService",
    "accept": "application/json, text/javascript, */*",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
}

logger = SgLogSetup().get_logger("chatrwireless_com")


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
    url = "https://1-dot-rogers-store-finder.appspot.com/searchChatrStoresService"
    payload = {
        "select": "ID,StoreName,City,Province,PostalCode,Address,Address2,Email,Fax,BusinessPhone,Phones,Vouchers,Accessories,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday,Latitude,Longitude,CONCAT(Longitude, ',' ,Latitude) as geometry,(6371 * acos(cos(radians(43.653226)) * cos(radians(Latitude)) * cos(radians(Longitude) - radians(-79.3831843)) + sin( radians(43.653226)) * sin(radians(Latitude)))) AS distance",
        "where": "Kiosk='1' AND (( 6371 * acos( cos( radians(43.653226) ) * cos( radians(Latitude) ) * cos( radians( Longitude ) - radians(-79.3831843) ) + sin( radians(43.653226) ) * sin( radians( Latitude ))))<5000)",
        "order": "distance ASC",
        "limit": "5000",
        "channelID": "CHATR",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "chatrwireless.com"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Record_ID":"' in line:
            items = line.split('"Record_ID":"')
            for item in items:
                if '"Store_Name":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"Store_Name":"')[1].split('"')[0]
                    add = item.split('"Address":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"Province":"')[1].split('"')[0]
                    zc = item.split('"Postal_Code":"')[1].split('"')[0]
                    try:
                        lng = item.split('"coordinates":[')[1].split(",")[0]
                        lat = (
                            item.split('"coordinates":[')[1].split(",")[1].split("]")[0]
                        )
                    except:
                        lng = "<MISSING>"
                        lat = "<MISSING>"
                    hours = "Sun: " + item.split('"Sunday":"')[1].split('"')[0]
                    hours = (
                        hours + "; Mon: " + item.split('"Monday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Tue: " + item.split('"Tuesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Wed: " + item.split('"Wednesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Thu: " + item.split('"Thursday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Fri: " + item.split('"Friday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Sat: " + item.split('"Saturday":"')[1].split('"')[0]
                    )
                    phone = item.split('"Business_Phone":"')[1].split('"')[0]
                    if phone == "":
                        phone = "<MISSING>"
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
