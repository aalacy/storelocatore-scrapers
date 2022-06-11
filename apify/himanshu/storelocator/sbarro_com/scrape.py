import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import usaddress
import lxml.html
from sglogging import sglog
from sgscrape import sgpostal as parser

logger = sglog.SgLogSetup().get_logger(logger_name="sbarro.com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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

        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    url_list = []
    base_url = "https://sbarro.com"
    UsState = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
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

    location_url = (
        "https://sbarro.com/locations/?user_search=62232&radius=2100&unit=MI&count=All"
    )
    soup = bs(session.get(location_url).text, "lxml")

    for link in soup.find_all("section", {"class": "locations-result"}):
        page_url = base_url + link.find("a")["href"]
        url_list.append(page_url)
        if page_url.split("/")[-1]:
            try:
                location_name = link.find("h1", {"class": "location-name"}).text.strip()
            except:
                location_name = link.find("h2", {"class": "location-name"}).text.strip()

            addr = list(
                link.find("p", {"class": "location-address nobottom"}).stripped_strings
            )

            if len(addr) == 1:
                address = usaddress.parse(addr[0])

                street_address = []
                city = ""
                state = ""
                zipp = ""
                for info in address:
                    if "SubaddressType" in info:
                        street_address.append(info[0])

                    if "SubaddressIdentifier" in info:
                        street_address.append(info[0])

                    if "Recipient" in info:
                        street_address.append(info[0])

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

                    if "PlaceName" in info:
                        city = info[0]
                    if "StateName" in info:
                        state = info[0]
                    if "ZipCode" in info:
                        zipp = info[0]

                street_address = " ".join(street_address)
            else:
                street_address = " ".join(addr[:-1])
                city = addr[-1].split(",")[0]
                try:
                    if len(addr[-1].split(",")[1].split()) == 2:
                        state = addr[-1].split(",")[1].split()[0]
                        zipp = addr[-1].split(",")[1].split()[-1]
                    else:
                        state = addr[-1].split(",")[1].split()[0]
                        zipp = "<MISSING>"
                except:
                    pass

            if link.find("div", {"class": "location-phone location-cta"}):
                phone = (
                    link.find("div", {"class": "location-phone location-cta"})
                    .find("span", {"class": "btn-label"})
                    .text.strip()
                )

            else:
                phone = "<MISSING>"

            store_number = link["id"].split("-")[-1].strip()
            lat = link["data-latitude"]
            if lat == "0":
                lat = "<MISSING>"

            lng = link["data-longitude"]
            if lng == "0":
                lng = "<MISSING>"

            location_type = "Restaurant"
            try:
                logger.info(page_url)
                location_soup = bs(session.get(page_url).text, "lxml")
                hours = " ".join(
                    list(
                        location_soup.find(
                            "div", {"class": "location-hours"}
                        ).stripped_strings
                    )
                ).replace("Hours of Operation", "")
                if "Hours not available" in hours:
                    hours = "<MISSING>"
            except:
                hours = "<MISSING>"
            if state in UsState:
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                if street_address in addressess:
                    continue
                addressess.append(street_address)
                yield store

    CA_states = [
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
        "YT",
        "NT",
        "NU",
    ]

    stores_req = session.get("https://sbarro.com/allstores.html")
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath("//div/a/@href")
    for store_url in stores:
        url_state = store_url.split("sbarro.com/locations/")[1].split("/")[0].strip()
        if url_state in CA_states:
            page_url = store_url
            url_list.append(page_url)
            store_req = session.get(page_url)
            if store_req.url == "https://sbarro.com/locations/":
                continue
            else:
                logger.info(page_url)
                store_sel = lxml.html.fromstring(store_req.text)
                location_name = "".join(
                    store_sel.xpath('//h1[@class="location-name "]/text()')
                ).strip()
                locator_domain = base_url
                address = "".join(
                    store_sel.xpath('//p[@class="location-address "]/text()')
                ).strip()
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                state = address.split(",")[-1].strip()
                zip = "<MISSING>"
                country_code = "CA"
                store_number = "<MISSING>"
                temp_phone = store_sel.xpath(
                    '//div[@class="location-phone location-cta"]//text()'
                )
                phone_list = []
                phone = ""
                for tmp in temp_phone:
                    if len("".join(tmp).strip()) > 0:
                        phone_list.append("".join(tmp).strip())

                if len(phone_list) > 0:
                    phone = phone_list[0]

                location_type = "Restaurant"
                latitude = "".join(
                    store_sel.xpath(
                        '//section[@class="locations-result"]/@data-latitude'
                    )
                ).strip()
                longitude = "".join(
                    store_sel.xpath(
                        '//section[@class="locations-result"]/@data-longitude'
                    )
                ).strip()
                hours_of_operation = ""
                hours = store_sel.xpath('//ul[@class="hours "]/li')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("span/text()")).strip()
                    time = "".join(hour.xpath("text()")).strip()
                    if "Hours not available" not in time:
                        hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                if store_number == "":
                    store_number = "<MISSING>"

                if location_name == "":
                    location_name = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"

                if phone == "" or phone is None:
                    phone = "<MISSING>"

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                if location_type == "":
                    location_type = "<MISSING>"

                curr_list = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                    page_url,
                ]
                yield curr_list

    location_url = "https://sbarro.com/locations/?user_search=United+Kingdom&radius=1000&unit=MI&count=5"
    soup = bs(session.get(location_url).text, "lxml")

    for link in soup.find_all("section", {"class": "locations-result"}):
        page_url = base_url + link.find("a")["href"]
        if page_url not in url_list:
            if page_url.split("/")[-1]:
                try:
                    location_name = link.find(
                        "h1", {"class": "location-name"}
                    ).text.strip()
                except:
                    location_name = link.find(
                        "h2", {"class": "location-name"}
                    ).text.strip()

                addr = list(
                    link.find(
                        "p", {"class": "location-address nobottom"}
                    ).stripped_strings
                )

                raw_address = ", ".join(addr)
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zipp = formatted_addr.postcode

                if link.find("div", {"class": "location-phone location-cta"}):
                    phone = (
                        link.find("div", {"class": "location-phone location-cta"})
                        .find("span", {"class": "btn-label"})
                        .text.strip()
                    )

                else:
                    phone = "<MISSING>"

                if phone == "-":
                    phone = "<MISSING>"

                store_number = link["id"].split("-")[-1].strip()
                lat = link["data-latitude"]
                if lat == "0":
                    lat = "<MISSING>"

                lng = link["data-longitude"]
                if lng == "0":
                    lng = "<MISSING>"

                location_type = "Restaurant"
                try:
                    logger.info(page_url)
                    location_soup = bs(session.get(page_url).text, "lxml")
                    hours = " ".join(
                        list(
                            location_soup.find(
                                "div", {"class": "location-hours"}
                            ).stripped_strings
                        )
                    ).replace("Hours of Operation", "")
                    if "Hours not available" in hours:
                        hours = "<MISSING>"
                except:
                    hours = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zipp == "" or zipp is None:
                    zipp = "<MISSING>"

                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("GB")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
