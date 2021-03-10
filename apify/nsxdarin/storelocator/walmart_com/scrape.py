import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from requests import exceptions  # noqa
from urllib3 import exceptions as urllibException

logger = SgLogSetup().get_logger("walmart_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=50,
)

def api_get(start_url, headers, timeout, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = session.post(start_url, headers=headers,  timeout=timeout)
    except exceptions.RequestException as requestsException:
        if "ProxyError" in str(requestsException):
            attempts += 1
            error = True
        else:
            raise requestsException
            
    except urllibException.SSLError as urllibException:
        if "BAD_RECORD_MAC" in str(e):
            attempts += 1
            error = True
        else:
            raise urllibException
        
    if error:
        if attempts < maxRetries:
            results = api_post(start_url, headers, timeout, attempts, maxRetries)
        else:
            TooManyRetries = "Retried "+str(maxRetres)+" times, got either SSLError or ProxyError" 
            raise TooManyRetries
    else:
        return results

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
    url = "https://www.walmart.com/sitemap_store_main.xml"
    ids = []
    session = SgRequests(proxy_rotation_failure_threshold=20)
    for code in search:
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.walmart.com/store/finder/electrode/api/stores?singleLineAddr="
            + code
            + "&distance=50"
        )
        website = "walmart.com"
        typ = "Walmart"
        try:
            r2 = session.get(url, headers=headers, timeout=15)
        except Exception:
            r2 = api_get(url,headers,15,0,15)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"storesData":{"stores"' in line2:
                items = line2.split('{"distance":')
                for item in items:
                    if '"buId":"' in item:
                        loc = item.split('"detailsPageURL":"')[1].split('"')[0]
                        name = (
                            item.split('"storeType":{"id":"')[0]
                            .rsplit('"displayName":"', 1)[1]
                            .split('"')[0]
                        )
                        phone = (
                            item.split('"storeType":{"id":"')[1]
                            .split('"phone":"')[1]
                            .split('"')[0]
                        )
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        store = loc.rsplit("/", 1)[1]
                        country = "US"
                        try:
                            hours = (
                                "Mon-Fri: "
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"monToFriHrs":')[1]
                                .split('"startHr":"')[1]
                                .split('"')[0]
                                + "-"
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"monToFriHrs":')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sat: "
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"saturdayHrs":')[1]
                                .split('"startHr":"')[1]
                                .split('"')[0]
                                + "-"
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"saturdayHrs":')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sun: "
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"sundayHrs":')[1]
                                .split('"startHr":"')[1]
                                .split('"')[0]
                                + "-"
                                + item.split('}}],"operationalHours":{"')[1]
                                .split('"sundayHrs":')[1]
                                .split('"endHr":"')[1]
                                .split('"')[0]
                            )
                        except:
                            hours = "<MISSING>"
                        lat = item.split('"geoPoint":{"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split("}")[0]
                        phone = item.split(',"phone":"')[1].split('"')[0]
                        if "Supercenter" in name:
                            typ = "Supercenter"
                        if "Neighborhood Market" in name:
                            typ = "Neighborhood Market"
                        if hours == "":
                            hours = "<MISSING>"
                        if add != "" and store not in ids:
                            ids.append(store)
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
