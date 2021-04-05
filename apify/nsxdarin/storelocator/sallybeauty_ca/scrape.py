import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sallybeauty_ca")

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
    ids = []
    canadaurls = [
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=49.895136&long=-97.13837439999999&searchKey=Winnipeg%2C%20ON",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=49.2827291&long=-123.1207375&searchKey=Vancouver%2C%20BC",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=45.5016889&long=-73.567256&searchKey=Montreal%2C%20QC",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=47.5615096&long=-52.7125768&searchKey=St.%20John%27s%2C%20NL",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=51.04473309999999&long=-114.0718831&searchKey=Calgary%2C%20AB",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=43.653226&long=-79.3831843&searchKey=Toronto%2C%20ON",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=46.258363&long=-63.1347069&searchKey=Charlottetown%2C%20PE",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=53.531658&long=-113.4544765&searchKey=Edmonton%2C%20AB",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=51.0419046&long=-104.8173439&searchKey=Regina%2C%20SK",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=48.4082055&long=-89.1815437&searchKey=Thunder%20Bay%2C%20ON",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=48.4256369&long=-71.075985&searchKey=Saguenay%2C%20QC",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=46.4256369&long=-81.075985&searchKey=Saguenay%2C%20QC",
        "https://www.sallybeauty.ca/on/demandware.store/Sites-SC-Site/en_CA/Stores-FindStores?showMap=true&radius=300&radius=300&lat=52.4256369&long=-81.075985&searchKey=Saguenay%2C%20QC",
    ]
    for curl in canadaurls:
        url = curl
        logger.info(("Pulling Canada URL %s..." % curl))
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ""
                loc = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                country = ""
                typ = "<MISSING>"
                lat = ""
                lng = ""
                phone = ""
                website = "sallybeauty.ca"
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + " " + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if "<div class='store-hours-day'>" in line:
                days = line.split("<div class='store-hours-day'>")
                for day in days:
                    if '<span class=\\"hours-of-day\\">' in day:
                        hrs = (
                            day.split(":")[0]
                            + ": "
                            + day.split('<span class=\\"hours-of-day\\">')[1].split(
                                "<"
                            )[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = line.split('"longitude": ')[1].split(",")[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                cas = [
                    "AB",
                    "BC",
                    "MB",
                    "NL",
                    "ON",
                    "NB",
                    "QC",
                    "PQ",
                    "SK",
                    "PE",
                    "PEI",
                ]
                if state in cas:
                    country = "CA"
            if "isBOPISEligibleStore" in line:
                if store not in ids and country == "CA":
                    ids.append(store)
                    loc = (
                        "https://www.sallybeauty.ca/store-details/?showMap=true&horizontalView=true&lat="
                        + lat
                        + "&long="
                        + lng
                    )
                    logger.info(("Pulling Store ID #%s..." % store))
                    if hours == "":
                        hours = "<MISSING>"
                    store = store.replace("store_", "")
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
