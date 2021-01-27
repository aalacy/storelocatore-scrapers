import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "marinemax_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    data = []    
    url = 'https://mes124x9ka-dsn.algolia.net/1/indexes/StoreLocations/query'
    params = {
        'x-algolia-api-key': '6a25958408aec66c81024ac2fcd3677c',
        'x-algolia-application-id': 'MES124X9KA',
        'x-algolia-agent': 'Algolia for vanilla JavaScript 3.7.0'
    }
    body = {"params": "query=&hitsPerPage=100&aroundLatLng=34.2156247%2C-77.8125942&aroundRadius=all"}
    loclist = session.post(url, params=params, json=body).json()
    loclist = loclist['hits']
    for loc in loclist:
            title = loc["DealerName"]
            link = loc["LocationPageURL"]
            if not link:
                link = "<MISSING>"
            phone = loc["PhoneNumber"]
            if not phone:
                phone = "<MISSING>"
            temp = loc ['Address2']
            if not temp:
                street = loc["Address1"]
            else:
                street = loc["Address1"]
                street = street + " " + temp
            city = loc["City"]
            state = loc["State"]
            pcode = loc["PostalCode"]
            ccode = loc["CountryCode"]
            longt = loc["_geoloc"]['lng']
            lat = loc["_geoloc"]['lat']
            store = loc["IDS_Site_ID"]
            data.append(
                [
                    "https://www.marinemax.com/",
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
                    "<MISSING>"
                ]
            )
    return data

def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")

scrape()
