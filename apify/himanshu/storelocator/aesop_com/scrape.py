import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import usaddress as usd
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aesop_com")
session = SgRequests()
tm = {
    "Recipient": "recipient",
    "AddressNumber": "address1",
    "AddressNumberPrefix": "address1",
    "AddressNumberSuffix": "address1",
    "StreetName": "address1",
    "StreetNamePreDirectional": "address1",
    "StreetNamePreModifier": "address1",
    "StreetNamePreType": "address1",
    "StreetNamePostDirectional": "address1",
    "StreetNamePostModifier": "address1",
    "StreetNamePostType": "address1",
    "BuildingName": "address1",
    "CornerOf": "address1",
    "IntersectionSeparator": "address1",
    "LandmarkName": "address1",
    "USPSBoxGroupID": "address1",
    "USPSBoxGroupType": "address1",
    "OccupancyType": "address1",
    "OccupancyIdentifier": "address1",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
    "SubaddressType": "address1",
    "SubaddressType": "address1",
    "SubaddressIdentifier": "address1",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "1219",
        "content-type": "application/json",
        "cookie": "_ga=GA1.2.645616883.1597646190; km_ai=BeKCTmTAzEQYMsjjEQzc%2BOsA844%3D; km_lv=x; __zlcmid=zljN2UOsa4uXUz; _gid=GA1.2.1155591714.1597915313; dtCookie==3=srv=3=sn=AF257B332CF10DE8BEDD4D79A565D59E=perc=100000=ol=0=mul=1; JSESSIONID=Y5-6f32ec93-30a4-41be-9559-286dfb052dfa; km_vs=1; _gaexp=GAX1.2.-zZx6Y7LQNiwJdQu8Tmq8g.18571.0; fs_uid=rs.fullstory.com#NAFZX#5089109635973120:4883790924300288/1629260786; kvcd=1598007050439; AWSALB=4xm5KW3hvUv48YrinuOrD+EbsIReAPVFNFP1qVECc1VLYK8UueFHZwTFhRuZM4sGXE9VZz+Ws3BamklnK3JozRhtx242h3rOtgVZV82Xl8kkOk2fzezwssJ6kQ00; AWSALBCORS=4xm5KW3hvUv48YrinuOrD+EbsIReAPVFNFP1qVECc1VLYK8UueFHZwTFhRuZM4sGXE9VZz+Ws3BamklnK3JozRhtx242h3rOtgVZV82Xl8kkOk2fzezwssJ6kQ00; _gat_UA-7103822-1=1",
        "origin": "https://www.aesop.com",
        "referer": "https://www.aesop.com/hk/en/?visitMenu=open&visit=Baltimore%2C%20MD%2021216%2C%20USA",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "x-api-key": "unPGMTFfsi1fyT9Fi03Ee6Ds5LMhatBh7LZtQ7o8",
        "x-locale": "en-HK",
        "x-preview": "false",
        "cache-control": "no-cache",
        "postman-token": "d06d2864-850d-65fb-6bce-d18d129d4a3c",
    }

    base_url = "https://www.aesop.com"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=100,
        max_search_results=100,
    )

    adressess = []
    for lat, lng in search:
        payload = (
            '{"query":"\\n  \\n  fragment openingHours on StoreOpeningHoursTimesType {\\n    closedAllDay\\n    openingTimeHour\\n    openingTimeMinute\\n    closingTimeHour\\n    closingTimeMinute\\n  }\\n\\n  query {\\n    stores (\\n      query: [\\n        { key: \\"fields.storeLocation\\", Op:WITHIN, value: \\"37.887,-79.488,'
            + str(lat)
            + ","
            + str(lng)
            + '\\" }\\n      ]\\n    ) {\\n      id\\n      address\\n      city\\n      combinedAddress: address\\n      country\\n      email\\n      facialAppointments\\n      facialAppointmentsLink\\n      type\\n      features: type\\n      formattedAddress\\n      image {\\n        large\\n        medium\\n        small\\n      }\\n      location {\\n        lat\\n        lon\\n      }\\n      name\\n      \\n  openingHours {\\n    monday {\\n      ...openingHours\\n    }\\n    tuesday {\\n      ...openingHours\\n    }\\n    wednesday {\\n      ...openingHours\\n    }\\n    thursday {\\n      ...openingHours\\n    }\\n    friday {\\n      ...openingHours\\n    }\\n    saturday {\\n      ...openingHours\\n    }\\n    sunday {\\n      ...openingHours\\n    }\\n  }\\n\\n      \\n  specialOpeningHours {\\n    date\\n    closedAllDay\\n    openingTimeHour\\n    openingTimeMinute\\n    closingTimeHour\\n    closingTimeMinute\\n  }\\n\\n      phone\\n    }\\n  }\\n"}'
        )

        location_url = "https://www.aesop.com/graphql"
        try:
            r = session.post(location_url, headers=headers, data=payload)
            json_data = r.json()["data"]["stores"]
        except:
            continue
        for value in json_data:
            country = ["GB", "HK", "KR", "JP", "TH", "TW"]
            if value["country"] not in country:
                loc_name = [
                    "Aesop Harbour City Facial Room",
                    "Aesop Tryano",
                    "Aesop Daimaru Shinsaibashi",
                    "Mitsukoshi A4",
                    "Aesop Korinbo Tokyu Square",
                    "Isetan Shinjuku Beauty Apothecary",
                    "Aesop New Town Plaza",
                    "Hyundai Daegu",
                    "Shilla Ipark DFS",
                    "Aesop Eslite Taichung Parklane",
                    "Aesop Hibiya Chanter",
                    "Aesop Hankyu Nishinomiya Gardens",
                    "Aesop Nakanoshima Festival Plaza",
                    "Aesop Nihonbashi Takashimaya S.C",
                    "Aesop Ginza SIX",
                    "Aesop Takashimaya Gate Tower Mall",
                    "Aesop Central Chidlom",
                    "Open Shop",
                    "Aesop Central Ladprao",
                    "Aesop Tokyo Facial Appointments",
                    "Aesop Kanazawa",
                    "Aesop Jiyugaoka",
                    "Aesop Daan",
                    "Aesop Central@CentralwOrld",
                    "Aesop Central Bangna",
                    "Aesop Emporium",
                    "Aesop Paragon",
                ]
                if value["name"] not in loc_name:

                    locator_domain = base_url
                    location_name = value["name"]
                    temp_add = value["formattedAddress"].replace(", Space B115", "")

                    if value["country"] == "CA":
                        if location_name == "Aesop Gastown":
                            street_address = "19 Water St."
                            city = "Vancouver"
                            state = "BC"
                            zipp = "V6B-1A1"
                        elif location_name == "Aesop Main Street":
                            street_address = "3583 Main Street, 200A"
                            city = "Vancouver"
                            state = "BC"
                            zipp = "V5V 3N4"
                        elif location_name == "A'Hoy":
                            street_address = "4391 Gallant Ave"
                            city = "North Vancouver"
                            state = "BC"
                            zipp = "<MISSING>"
                        elif location_name == "Holt Renfrew Yorkdale":
                            street_address = "3401 Dufferin Street"
                            city = "Toronto"
                            state = "ON"
                            zipp = "M6A 2T9"
                        elif location_name == "Aesop Petite Bourgogne":
                            street_address = "2493 Rue Notre-Dame Ouest"
                            city = "Montréal"
                            state = "QC"
                            zipp = "H3J 1N6"
                        elif location_name == "Aesop Toronto Eaton Centre":
                            street_address = value["address"]
                            city = value["city"]
                            state = "ON"
                            zipp = "M5B-2H1"
                        elif location_name == "Aesop Mile End":
                            street_address = value["address"]
                            city = value["city"]
                            state = "QC"
                            zipp = "H2V-1Y1"
                        else:
                            ca_add = temp_add.split(",")
                            street_address = ca_add[0]
                            city = ca_add[1].strip()

                            tem_state_zip = ca_add[2].strip().split(" ")
                            if len(tem_state_zip) == 3:
                                state = tem_state_zip[0]
                                zipp = "-".join(tem_state_zip[1:])
                            elif len(tem_state_zip) == 2:
                                zipper = []
                                zipper[:] = tem_state_zip[-1]
                                if len(zipper) == 7:
                                    state = tem_state_zip[0]
                                    zipp = tem_state_zip[-1]
                                else:
                                    state = "<MISSING>"
                                    zipp = "-".join(tem_state_zip)
                        country_code = "CA"
                    elif value["country"] == "US":
                        if location_name == "Madison Hall":
                            street_address = "CAA Hotel/ 12 S Michigan Ave"
                            city = value["city"]
                            state = "IL"
                            zipp = "<MISSING>"
                        elif location_name == "Aesop Santa Monica Place":
                            street_address = temp_add.split(",")[0]
                            city = value["city"]
                            state = "CA"
                            zipp = "90401"
                        elif location_name == "Aesop Chelsea":
                            street_address = "174 Ninth Avenue"
                            city = value["city"]
                            state = "NY"
                            zipp = "10011"
                        elif location_name == "Raleigh Denim":
                            street_address == "319 W. Martin St"
                            city = value["city"]
                            state = "NC"
                            zipp = "27601"
                        elif location_name == "Aesop Fashion Valley":
                            street_address = value["address"]
                            city = value["city"]
                            state = "CA"
                            zipp = "92108"
                        elif location_name == "In The Field":
                            street_address = "730 East Ojai Avenue"
                            city = value["city"]
                            state = "<MISSING>"
                            zipp = "93023"
                        elif location_name == "Aesop Newbury Street":
                            street_address = value["address"]
                            city = value["city"]
                            state = "MA"
                            zipp = "02116"
                        else:
                            addr_format = usd.tag(temp_add, tm)
                            addr = list(addr_format[0].items())
                            street_address = addr[0][1]
                            city = addr[1][1]
                            if value["city"] == "Brooklyn":
                                state = "NY"
                            else:
                                state = addr[2][1].split(",")[0]
                            try:
                                zipp = addr[3][1]
                            except IndexError:
                                zipp = "<MISSING>"
                        country_code = "US"

                    elif value["country"] is None:
                        if location_name == "Aesop UTC":
                            street_address = (
                                "Space 2118, Westfield, 4545 La Jolla Village Drive"
                            )
                            city = "San Diego"
                            state = "CA"
                            zipp = "92122"
                            country_code = "US"
                        elif (
                            location_name == "Aesop Vieux-Montréal"
                            or location_name == "Nordstrom Yorkdale"
                            or location_name == "Nordstrom Eatons Centre"
                        ):

                            ca_add = temp_add.split(",")
                            street_address = ca_add[0]
                            country_code = "CA"
                            city = ca_add[1].strip()
                            tem_state_zip = ca_add[2].strip().split(" ")
                            if len(tem_state_zip) == 3:
                                state = tem_state_zip[0]
                                zipp = "-".join(tem_state_zip[1:])
                            elif len(tem_state_zip) == 2:
                                zipper = []
                                zipper[:] = tem_state_zip[-1]
                                if len(zipper) == 7:
                                    state = tem_state_zip[0]
                                    zipp = tem_state_zip[-1]
                                else:
                                    state = "<MISSING>"
                                    zipp = "-".join(tem_state_zip)
                            country_code = "CA"
                        else:
                            addr_format = usd.tag(temp_add, tm)
                            addr = list(addr_format[0].items())
                            street_address = addr[0][1]
                            country_code = "US"
                            city = addr[1][1]
                            if value["city"] == "Brooklyn":
                                state = "NY"
                            else:
                                state = addr[2][1].split(",")[0]
                            try:
                                zipp = addr[3][1]
                            except IndexError:
                                zipp = "<MISSING>"
                            country_code = "US"

                    else:
                        continue

                    store_number = "<MISSING>"
                    if value["phone"] == "":
                        phone = "<MISSING>"
                    else:
                        try:
                            phone = value["phone"].replace(" Ext. 1", "")
                        except:
                            phone = "<MISSING>"
                    location_type = value["type"]
                    latitude = value["location"]["lat"]
                    longitude = value["location"]["lon"]
                    try:

                        h = value["openingHours"]

                        if h["monday"]["closedAllDay"] is True:
                            monday = "closed"
                        else:
                            monday = (
                                h["monday"]["openingTimeHour"]
                                + ":"
                                + h["monday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["monday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["monday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["tuesday"]["closedAllDay"] is True:
                            tuesday = "closed"
                        else:
                            tuesday = (
                                h["tuesday"]["openingTimeHour"]
                                + ":"
                                + h["tuesday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["tuesday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["tuesday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["wednesday"]["closedAllDay"] is True:
                            wednesday = "closed"
                        else:
                            wednesday = (
                                h["wednesday"]["openingTimeHour"]
                                + ":"
                                + h["wednesday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["wednesday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["wednesday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["thursday"]["closedAllDay"] is True:
                            thursday = "closed"
                        else:
                            thursday = (
                                h["thursday"]["openingTimeHour"]
                                + ":"
                                + h["thursday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["thursday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["thursday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["friday"]["closedAllDay"] is True:
                            friday = "closed"
                        else:
                            friday = (
                                h["friday"]["openingTimeHour"]
                                + ":"
                                + h["friday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["friday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["friday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["saturday"]["closedAllDay"] is True:
                            saturday = "closed"
                        else:
                            saturday = (
                                h["saturday"]["openingTimeHour"]
                                + ":"
                                + h["saturday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["saturday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["saturday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        if h["sunday"]["closedAllDay"] is True:
                            sunday = "closed"
                        else:
                            sunday = (
                                h["sunday"]["openingTimeHour"]
                                + ":"
                                + h["sunday"]["openingTimeMinute"].replace("0", "00")
                                + "AM"
                                + "-"
                                + str(int(h["sunday"]["closingTimeHour"]) - 12)
                                + ":"
                                + h["sunday"]["closingTimeMinute"].replace("0", "00")
                                + "PM"
                            )

                        hours_of_operation = (
                            "monday-"
                            + monday
                            + ", tuesday-"
                            + tuesday
                            + ", wednesday-"
                            + wednesday
                            + ", thursday-"
                            + thursday
                            + ", friday-"
                            + friday
                            + ", saturday-"
                            + saturday
                            + ", sunday-"
                            + sunday
                        )
                    except:
                        hours_of_operation = "<MISSING>"

                    if location_type == "Signature Store":
                        page_url = "https://www.aesop.com/hk/en/r/" + value["id"]
                    else:
                        page_url = "<MISSING>"

                    store = []
                    if street_address == "Space":
                        street_address = "Space 2118, Westfield, 4545 La Jolla"
                        state = "Village Drive"
                        city = "San Diego"
                        zipp = "92122"
                    store.append(locator_domain)
                    store.append(location_name)
                    store.append(
                        street_address.replace(
                            "630 Old Country Rd", "630 Old Country Rd Space, 1101D"
                        )
                        .replace("International Market Place, Space 116, ", "")
                        .replace("NorthPark Center, ", "")
                        .replace("Space 2118, ", "")
                        .replace("Space K02 - ", "")
                        .replace("The Village at Corte Madera, Space D207, ", "")
                        .replace("Tysons Corner Center, Suite O008U, ", "")
                        .replace("Westfield, ", "")
                    )
                    store.append(city.replace("Space, 1101D ", ""))
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(
                        hours_of_operation if hours_of_operation else "<MISSING>"
                    )
                    store.append(page_url)
                    if store[2] in adressess:
                        continue
                    adressess.append(store[2])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
