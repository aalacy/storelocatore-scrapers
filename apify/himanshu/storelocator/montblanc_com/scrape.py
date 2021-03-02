import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("montblanc_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressesess = []
    for q in range(1, 5):
        url = (
            "https://www.montblanc.com/api/richemont1//wcs/resources/store/montblanc_US/storelocator/boutiques?pageSize=1000&pageNumber="
            + str(q)
        )
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "referer": "https://www.montblanc.com/en-us/store-locator",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
            "x-dtpc": "4$191667465_950h12vQPNFURNDJMQINMBHSQMRENURORTBHPHM-0e9",
            "x-ibm-client-id": "b8d40347-fa4e-457c-831a-31b159bf081a",
            "x-requested-with": "XMLHttpRequest",
        }

        response = session.get(url, headers=headers).json()
        for data in response["data"]:
            try:
                if (
                    data["address"]["countryCode"] == "CA"
                    or data["address"]["countryCode"] == "US"
                    or data["address"]["countryCode"] == "USA"
                    or data["address"]["countryCode"] == "GB"
                ):
                    if "Reseller" != data["attributes"][0]["values"][0]["value"]:
                        raw_address = data["address"]["line1"]
                        raw_address1 = raw_address
                        countryCode = data["address"]["countryCode"]
                        if countryCode == "GB":
                            countryCode = "UK"
                        else:
                            countryCode = data["address"]["countryCode"]
                        if "phone1" in data["address"]:
                            phone = data["address"]["phone1"]
                        else:
                            phone = ""
                        hours = ""
                        location_name = data["storeName"]
                        page_url = "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/" + location_name.lower().replace(
                            "-", ""
                        ).replace(
                            " ", "-"
                        )
                        page_url = (
                            page_url.replace("--", "-")
                            .replace("--tyson's", "-tyson-s")
                            .replace("--", "-")
                            .replace("'s", "-s")
                            .replace("o'", "o-")
                        )

                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-orlando-millenia"
                            in page_url
                        ):
                            continue
                        if (
                            "Washington DC Tyson's Galleria 2001 International Drive, Suite 2134 McLean, VA 22102"
                            in raw_address
                        ):
                            page_url = "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-mc-lean-tyson-s"
                        response1 = bs(session.get(page_url).text, "lxml")
                        try:
                            hours = (
                                " ".join(
                                    list(
                                        response1.find(
                                            "div",
                                            {
                                                "class": re.compile(
                                                    "mb-singleStore__openingColumn"
                                                )
                                            },
                                        ).stripped_strings
                                    )
                                )
                                .replace("Opening hours", "")
                                .strip()
                            )
                        except:
                            hours = "<MISSING>"
                        zipp = data["address"]["postCode"]
                        latitude = data["spatialData"]["latitude"]
                        longitude = data["spatialData"]["longitude"]
                        address = usaddress.parse(
                            raw_address.replace(zipp, "")
                            .replace(", Canada", "")
                            .replace("Canada,", "")
                            .replace("Canada", "")
                            .replace(", USA", "")
                            .replace("USA", "")
                        )
                        street_address = []
                        for info in address:
                            if "International" in info:
                                street_address.append(info[0])

                            if "BuildingName" in info:
                                street_address.append(info[0])

                            if "AddressNumber" in info:
                                street_address.append(info[0])

                            if "StreetNamePreDirectional" in info:
                                street_address.append(info[0])

                            if "StreetNamePreType" in info:
                                street_address.append(info[0])
                            if "StreetName" in info:
                                street_address.append(info[0])
                            if "StreetNamePostType" in info:
                                street_address.append(info[0])
                            if "StreetNamePostDirectional" in info:
                                street_address.append(info[0])
                            if "OccupancyType" in info:
                                street_address.append(info[0])
                            if "OccupancyIdentifier" in info:
                                street_address.append(info[0])

                        raw_address = (
                            " ".join(street_address)
                            .replace(",", "")
                            .replace("Ave.", "Avenue")
                            .replace(
                                "120 Grant Avenue", "120 Grant Avenue San Francisco"
                            )
                            .replace(
                                "160 North Gulph Road",
                                "King of Prussia Mall 160 North Gulph Road, Space #2160 B King of Prussia",
                            )
                            .replace(
                                "The Gardens Mall 3101 PGA Boulevard",
                                "The Gardens Mall 3101 PGA Boulevard, Space M-203 Palm Beach Gardens",
                            )
                            .replace(
                                "The Mall at Millenia 4200 Conroy Road",
                                "The Mall at Millenia 4200 Conroy Road, Space C-182 Orlando",
                            )
                            .replace(
                                "Dadeland Mall 7481 SW 88th Street Unit 1940",
                                "Dadeland Mall 7481 SW 88th Street Unit 1940 Miami",
                            )
                            .replace(
                                "2001 International International Drive Suite 2134 McLean",
                                "2001 International Drive, Suite 2134 McLean",
                            )
                            .replace(
                                "3327 Las Vegas Boulevard South Suite 2746",
                                "3327 Las Vegas Boulevard South, Suite 2746",
                            )
                            .replace(
                                "Ala Moana Center 1450 Ala Moana Boulevard Ste 2215 Honolulu",
                                "Ala Moana Center 1450 Ala Moana Boulevard Ste 2215",
                            )
                            .replace(
                                "International K2",
                                r"OHare International Airport Terminal 3, Concourse K, Gate K2 Chicago",
                            )
                        )
                        state = data["address"]["state"]
                        city = data["address"]["city"]
                        if phone == "-0":
                            phone = "<MISSING>"
                        store = []
                        zipp = zipp.split(" ")
                        if zipp[0] == "0":
                            zipp = "<MISSING>"
                        elif zipp[-1].isdigit():
                            zipp = zipp[-1]
                        else:
                            zipp = " ".join(zipp)
                        store_number = ""
                        store.append("https://www.montblanc.com/")
                        store.append(location_name)
                        store.append(
                            raw_address.replace(" Tampa", "")
                            .replace("1200 Scottsdale", "1200 ")
                            .replace("Gate K2 Chicago", "Gate K2")
                            .replace(
                                "Cherry Creek Shopping Center 3000 East First Avenue Denver",
                                "Cherry Creek Shopping Center 3000 East First Avenue",
                            )
                            .replace(
                                "120 Grant Avenue San Francisco", "120 Grant Avenue"
                            )
                            .replace(
                                "Lenox Square 3393 Peachtree Road North",
                                "Lenox Square 3393 Peachtree Road North East  #3006 Atlanta",
                            )
                            .replace("Space M-203 Palm Beach Gardens", "Space M-203 ")
                            .replace(", Space C-182 Orlando", ", Space C-182 ")
                            .replace(
                                "Dadeland Mall 7481 SW 88th Street Unit 1940 Miami",
                                "Dadeland Mall 7481 SW 88th Street Unit 1940",
                            )
                            .replace("Suite 2134 McLean", "Suite 2134 ")
                            .replace(
                                "Vegas Boulevard South Las Vegas",
                                "Vegas Boulevard South",
                            )
                            .replace("International International Plaza ", "")
                            .replace("Fashion Square ", "")
                            .replace("Valley Fair Center ", "")
                            .replace("North Star Mall ", "")
                            .replace("King of Prussia Mall", "")
                            .replace("The Gardens Mall ", "")
                            .replace("The Mall at Millenia ", "")
                            .replace("Dadeland Mall ", "")
                            .replace("Beverly Center ", "")
                            .replace("Roosevelt Field Mall ", "")
                            .replace("The Forum Shops at Caesars ", "")
                            .replace("Ala Moana Center ", "")
                            .replace("Cherry Creek Shopping Center", "")
                            .replace("NorthPark Center ", "")
                            .replace("South Coast Plaza ", "")
                            .replace("O'Hare ", "")
                            .replace("South Park Mall ", "")
                            .replace("Copley Place ", "")
                            .replace("Town Center at Boca Raton", "")
                            .replace("Lenox Square ", "")
                            .replace(
                                "South Coast Plaza 3333 Bristol Street Ste. # 2209 Costa Mesa",
                                "South Coast Plaza 3333 Bristol Street Ste. # 2209",
                            )
                            .replace(" #3006 Atlanta", " #3006 ")
                            .replace(
                                "he Mall at Millenia 4200 Conroy Road",
                                "The Mall at Millenia 4200 Conroy Road Space C -182",
                            )
                        )
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append(countryCode)
                        store.append(store_number)
                        store.append(phone)
                        store.append("Boutique")
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours.strip())
                        store.append(page_url)
                        store = [str(x).strip() if x else "<MISSING>" for x in store]

                        if str(raw_address1 + page_url) in addressesess:
                            continue
                        addressesess.append(str(raw_address1 + page_url))
                        yield store
            except:
                continue


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
fetch_data()
