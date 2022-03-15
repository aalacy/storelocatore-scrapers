from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

session = SgRequests()

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

session = SgRequests()

for search_lat, search_lon in search:
    url = (
        "https://platform.cloud.coveo.com/rest/search/v2?organizationId=caleresproduction4uzryqju&actionsHistory=%5B%5D&referrer=&visitorId=27a589ed-4a45-4be0-b57c-ef5467374d32&isGuestUser=false&aq=(%24qf(function%3A'dist(%40latitude%2C%20%40longitude%2C%20"
        + str(search_lat)
        + "%2C%20"
        + str(search_lon)
        + ")'%2C%20fieldName%3A%20'distance'))%20(%40distance%3C%3D10000000)%20(%40source%3D%3D(%22Coveo_web_index%20-%20ecom930-prd-coveo%22%2C20000_FamousFootwear))&cq=%40source%3D%3D20000_FamousFootwear&searchHub=FamousStoreLocator&locale=en&maximumAge=900000&firstResult=0&numberOfResults=170&excerptLength=200&enableDidYouMean=false&sortCriteria=%40distance%20ascending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&facetOptions=%7B%7D&categoryFacets=%5B%5D&retrieveFirstSentences=true&timezone=America%2FNew_York&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&context=%7B%22device%22%3A%22Default%22%2C%22isAnonymous%22%3A%22true%22%2C%22website%22%3A%22FamousFootwear%22%7D&allowQueriesWithoutKeywords=true"
    )

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer xx6b22c1da-b9c6-495b-9ae1-e3ac72612c6f",
        "content-type": 'application/x-www-form-urlencoded; charset="UTF-8"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
    }

    response = session.post(url, headers=headers).json()

    for location in response["results"]:

        locator_domain = "famousfootwear.com"
        page_url = "famousfootwear.com" + location["raw"]["storedetailurl"]
        location_name = location["title"]
        address = location["raw"]["address1"]

        if "address2" in location["raw"].keys():
            address = address + " " + location["raw"]["address2"]
        city = location["raw"]["city"]
        state = location["raw"]["state"]

        zipp = location["raw"]["zipcode"][:5]
        country_code = "US"
        store_number = location["raw"]["storeid"]
        phone = location["raw"]["phonenumber"]
        location_type = location["raw"]["objecttype"]
        latitude = location["raw"]["latitude"]
        longitude = location["raw"]["longitude"]

        hours = (
            "Mon "
            + location["raw"]["mondayhours"]
            + ", Tue "
            + location["raw"]["tuesdayhours"]
            + ", Wed "
            + location["raw"]["wednesdayhours"]
            + ", Thu "
            + location["raw"]["thursdayhours"]
            + ", Fri "
            + location["raw"]["fridayhours"]
            + ", Sat "
            + location["raw"]["saturdayhours"]
            + ", Sun "
            + location["raw"]["sundayhours"]
        )

        search.found_location_at(latitude, longitude)

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(address)
        citys.append(city)
        states.append(state)
        zips.append(zipp)
        country_codes.append(country_code)
        phones.append(phone)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        store_numbers.append(store_number)
        hours_of_operations.append(hours)

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "country_code": country_codes,
        "location_type": location_types,
        "hours_of_operation": hours_of_operations,
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
