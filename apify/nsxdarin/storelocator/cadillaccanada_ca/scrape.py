import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("cadillaccanada_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "locale": "en_US",
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


search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=None,
    max_search_results=10,
)


def fetch_data():
    ids = []
    for zipcode in search:
        url = (
            "https://www.cadillacoffers.ca/apps/leap/readDealersJson?searchType=postalCodeSearch&postalCode="
            + zipcode.replace(" ", "%20")
            + "&language=en&pagePath=%2Fcontent%2Fcadillac-offers%2Fca%2Fen%2Fdealer-locations&_=1604593530983"
        )
        logger.info("Pulling Code %s..." % zipcode)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"dealerCode":"' in line:
                items = line.split('"dealerCode":"')
                for item in items:
                    if '"cpoisId":"' in item:
                        name = item.split('"dealerName":"')[1].split('"')[0]
                        store = item.split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        add = item.split('"streetAddress1":"')[1].split('"')[0]
                        if '"streetAddress2":"' in item:
                            add = (
                                add
                                + " "
                                + item.split('"streetAddress2":"')[1].split('"')[0]
                            )
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        country = "CA"
                        try:
                            phone = item.split('"primaryPhone":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        if phone == "<MISSING>":
                            try:
                                phone = item.split('"salesPhone":"')[1].split('"')[0]
                            except:
                                phone = "<MISSING>"
                        typ = "Dealer"
                        try:
                            purl = item.split('"websiteURL":"')[1].split('"')[0]
                        except:
                            purl = "<MISSING>"
                        website = "cadillaccanada.ca"
                        try:
                            hours = (
                                "Sun: Closed; Mon: "
                                + item.split('"salesMondayOpen":"')[1].split('00"')[0]
                                + "-"
                                + item.split('"salesMondayClose":"')[1].split('00"')[0]
                            )
                            hours = (
                                hours
                                + "; Tue:"
                                + item.split('"salesTuesdayOpen":"')[1].split('00"')[0]
                                + "-"
                                + item.split('"salesTuesdayClose":"')[1].split('00"')[0]
                            )
                            hours = (
                                hours
                                + "; Wed:"
                                + item.split('"salesWednesdayOpen":"')[1].split('00"')[
                                    0
                                ]
                                + "-"
                                + item.split('"salesWednesdayClose":"')[1].split('00"')[
                                    0
                                ]
                            )
                            hours = (
                                hours
                                + "; Thu:"
                                + item.split('"salesThursdayOpen":"')[1].split('00"')[0]
                                + "-"
                                + item.split('"salesThursdayClose":"')[1].split('00"')[
                                    0
                                ]
                            )
                            hours = (
                                hours
                                + "; Fri:"
                                + item.split('"salesFridayOpen":"')[1].split('00"')[0]
                                + "-"
                                + item.split('"salesFridayClose":"')[1].split('00"')[0]
                            )
                            try:
                                hours = (
                                    hours
                                    + "; Sat:"
                                    + item.split('"salesSaturdayOpen":"')[1].split(
                                        '00"'
                                    )[0]
                                    + "-"
                                    + item.split('"salesSaturdayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                            except:
                                hours = hours + "; Sat: Closed"
                        except:
                            hours = "<MISSING>"
                        if store not in ids:
                            ids.append(store)
                            logger.info("Pulling Store ID #%s..." % store)
                            yield [
                                website,
                                purl,
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
