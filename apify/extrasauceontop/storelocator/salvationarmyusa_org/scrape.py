# Import dependencies
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import pandas as pd


def getdata():
    # Initiate session, sgzip search object and base url
    session = SgRequests()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_results=30
    )
    base_url = "https://public.api.gdos.salvationarmy.org/search"

    # initiate needed lists
    page_urls = []
    locator_domains = []
    country_codes = []
    location_types = []
    names = []
    addresses = []
    citys = []
    states = []
    zips = []
    phones = []
    hours = []
    store_numbers = []
    lats = []
    lngs = []

    # Begin the loop
    x = 0
    for lat_lon in search:

        params = {
            "isoCountry": "us",
            "lat": lat_lon[0],
            "lng": lat_lon[1],
            "distanceUnits": "MILES",
            "limit": 30,
        }

        response = session.get(base_url, params=params).json()

        for location in response["objects"]:
            location_domain = "salvationarmyusa.org"
            country_code = "US"
            hour = "<MISSING>"
            store_number = "<MISSING>"
            page_url = (
                "https://public.api.gdos.salvationarmy.org/search?isoCountry=us&lat="
                + str(lat_lon[0])
                + "&lng="
                + str(lat_lon[1])
                + "&distanceUnits=MILES&limit=30"
            )

            name = location["name"]
            street = location["address1"]
            if street.split(" ")[0] == "Service":
                street = location["address2"]
            city = location["city"]
            state = location["state"]["shortCode"]
            zipp = location["displayZip"]
            if len(zipp) == 4:
                zipp == "0" + zipp
            phone = location["phoneNumber"]
            if phone == "":
                phone == "<MISSING>"
            lat = location["location"]["latitude"]
            lng = location["location"]["longitude"]

            # Create copies of location data for each service offered at a location
            servenum = len(location["services"])

            if servenum > 0:
                for service in location["services"]:
                    locator_domains.append(location_domain)
                    page_urls.append(page_url)
                    country_codes.append(country_code)
                    hours.append(hour)
                    store_numbers.append(store_number)

                    names.append(name)
                    addresses.append(street)
                    citys.append(city)
                    states.append(state)
                    zips.append(zipp)
                    phones.append(phone)
                    lats.append(lat)
                    lngs.append(lng)

                    location_types.append(service["category"]["name"])

            else:
                locator_domains.append(location_domain)
                page_urls.append(page_url)
                country_codes.append(country_code)
                hours.append(hour)
                store_numbers.append(store_number)

                names.append(name)
                addresses.append(street)
                citys.append(city)
                states.append(state)
                zips.append(zipp)
                phones.append(phone)
                lats.append(lat)
                lngs.append(lng)

                location_types.append("<MISSING>")

        # if x == 500:
        #     break
        x = x + 1
        print(x)

    df = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": names,
            "latitude": lats,
            "longitude": lngs,
            "street_address": addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "phone": phones,
            "hours_of_operation": hours,
            "country_code": country_codes,
            "location_type": location_types,
            "store_number": store_numbers,
        }
    )

    writedata(df)


def writedata(df):
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


getdata()
