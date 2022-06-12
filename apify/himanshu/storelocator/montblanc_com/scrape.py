import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("montblanc_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
                        location_name = data["storeName"]
                        street_address = data["address"]["line1"]
                        city = data["address"]["city"]
                        state = data["address"]["state"].replace("0", "<MISSING>")
                        zipp = data["address"]["postCode"].replace("IL 60666", "60666")
                        if zipp == "0":
                            zipp = "<MISSING>"
                        else:
                            zipp = data["address"]["postCode"].replace(
                                "IL 60666", "60666"
                            )
                        country_code = data["address"]["countryCode"]
                        if country_code == "GB":
                            country_code = "UK"
                        else:
                            country_code = data["address"]["countryCode"]
                        store_number = data["storeNumber"]
                        if "phone1" in data["address"]:
                            phone = (
                                data["address"]["phone1"]
                                .replace("-0", "<MISSING>")
                                .replace(" ", "")
                            )
                        else:
                            phone = "<MISSING>"
                        location_type = "Boutiques"
                        latitude = data["spatialData"]["latitude"]
                        longitude = data["spatialData"]["longitude"]

                        if country_code == "US":
                            page_url = "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/" + location_name.lower().replace(
                                "-", " "
                            ).replace(
                                "  ", " "
                            ).replace(
                                " ", "-"
                            ).replace(
                                "--", "-"
                            )
                        else:
                            page_url = "https://www.montblanc.com/en-gb/store-locator/stores/europe/united-kingdom/" + location_name.lower().replace(
                                "-", " "
                            ).replace(
                                "  ", " "
                            ).replace(
                                " ", "-"
                            ).replace(
                                "--", "-"
                            )

                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-aventura-aventura-mall"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-us/store-locator/stores/america/united-states/montblanc-aventura-mall"
                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-boutique-mclean-–-tyson's-galleria"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-us/store-locator/stores/america/united-states/montblanc-mc-lean-tyson-s"
                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-chicago-o'hare"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-us/store-locator/stores/america/united-states/montblanc-chicago-o-hare"
                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-las-vegas-caesar's"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-us/store-locator/stores/america/united-states/montblanc-las-vegas-caesar-s"
                        if (
                            "https://www.montblanc.com/en-ar/store-locator/stores/america/united-states/montblanc-new-york-westfield-world-trade-center"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-us/store-locator/stores/america/united-states/montblanc-new-york-world-trade-center"
                        if (
                            "https://www.montblanc.com/en-gb/store-locator/stores/europe/united-kingdom/selfridges"
                            in page_url
                        ):
                            page_url = "https://www.montblanc.com/en-gb/store-locator/stores/europe/united-kingdom/montblanc-boutique-london-selfridges"

                        r = session.get(page_url, headers=headers)
                        response1 = bs(r.text, "lxml")
                        try:
                            temp_hours_of_operation = response1.find(
                                "div", class_="mb-singleStore__openingColumn"
                            )
                            if temp_hours_of_operation is None:
                                hours_of_operation = "<MISSING>"
                            else:
                                hours_of_operation = (
                                    " ".join(
                                        list(
                                            response1.find(
                                                "div",
                                                class_="mb-singleStore__openingColumn",
                                            ).stripped_strings
                                        )
                                    )
                                    .replace("Opening hours", "")
                                    .strip()
                                )
                        except:
                            hours_of_operation = "<MISSING>"

                        street_address = (
                            street_address.replace(city, "")
                            .replace(state, "")
                            .replace(zipp, "")
                            .strip()
                        )

                        store = []
                        store.append("https://www.montblanc.com/")
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append(country_code)
                        store.append(store_number)
                        store.append(phone)
                        store.append(location_type)
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours_of_operation)
                        store.append(page_url)
                        store = [str(x).strip() if x else "<MISSING>" for x in store]
                        yield store
            except:
                pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
