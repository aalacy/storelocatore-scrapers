import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    session = SgRequests()

    state_list = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    data = []
    locator_domain = "johnstonesupply.com"

    for s in state_list:
        base_link = (
            "https://johnstonesupply.com/rest/js-store/lookupStoreBy?state=%s"
            % s.lower()
        )
        stores = session.get(base_link, headers=headers).json()

        for store in stores:
            location_name = store["description"]
            street_address = store["streetAddress"].strip()
            city = store["city"]
            state = store["state"]
            zip_code = store["zipCode"]
            country_code = "US"
            store_number = store["storeCode"]
            location_type = "<MISSING>"
            phone = store["phoneNumber"].split("<")[0].split(" (")[0].strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            link = "https://www.johnstonesupply.com/store%s/contact-us" % (store_number)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            got_res = False
            hours_of_operation = "<MISSING>"
            results = base.find_all(class_="col-7 col-md-9 col-lg-8")
            if results:
                for res in results:
                    if "#" in res.p.text:
                        if "#" + store_number in res.p.text:
                            got_res = True
                            break
                    elif (
                        location_name.split("-")[0].strip()
                        in res.p.text.replace("nio - Bro", "nio Bro").strip()
                    ):
                        got_res = True
                        break
                    else:
                        if street_address in res.find(class_="d-block").text:
                            got_res = True
                            break
                if got_res:
                    try:
                        hours_of_operation = (
                            " ".join(
                                list(res.find(class_="text-875rem").stripped_strings)
                            )
                            .replace("\r\n", " ")
                            .replace("  ", " ")
                            .strip()
                        )
                    except:
                        pass
            else:
                results = base.find_all(class_="card h-100")
                if results:
                    for res in results:
                        if "#" in res.find(class_="card-title mb-0").text:
                            if (
                                store_number
                                == res.find(class_="card-title mb-0").text.split("#")[
                                    -1
                                ]
                            ):
                                got_res = True
                                break
                    if got_res:
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        res.find(
                                            class_="text-darkblue"
                                        ).stripped_strings
                                    )
                                )
                                .replace("\r\n", " ")
                                .replace("  ", " ")
                                .strip()
                            )
                        except:
                            pass
                    try:
                        map_link = res.iframe["src"]
                        lat_pos = map_link.rfind("!3d")
                        latitude = map_link[
                            lat_pos + 3 : map_link.find("!", lat_pos + 5)
                        ].strip()
                        lng_pos = map_link.find("!2d")
                        longitude = map_link[
                            lng_pos + 3 : map_link.find("!", lng_pos + 5)
                        ].strip()
                    except:
                        pass
            hours_of_operation = (
                hours_of_operation.split("After Hours")[0]
                .split("24 Hour Emergency")[0]
                .split("Emergency")[0]
                .split("(Saturday)")[0]
                .replace("—", "-")
                .replace("Hours:", "")
                .strip()
            )

            # Store data
            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    # Canada
    base_link = "https://johnstonesupply.com/"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="modalFindStoreCanada").find_all(
        class_="row mb-3 border-bottom pb-3 modal-store-result"
    )
    for item in items:
        location_name = item.p.text.strip()
        street_address = item.p.text.strip()
        city = item.find(class_="d-block").text.split(",")[0].strip()
        state = item.find(class_="d-block").text.split(",")[1].split()[0].strip()
        zip_code = item.find(class_="d-block").text[-8:].strip()
        country_code = "CA"
        store_number = item.find_all("a")[-1]["href"].split("tore")[1]
        location_type = "<MISSING>"
        phone = item.find_all("a")[-2].text
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        link = "https://www.johnstonesupply.com/store%s/contact-us" % (store_number)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = "<MISSING>"
        results = base.find_all(class_="col-7 col-md-9 col-lg-8")
        for res in results:
            if store_number == res.p.text.split("#")[-1]:
                hours_of_operation = " ".join(
                    list(res.find(class_="text-875rem").stripped_strings)
                )

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
