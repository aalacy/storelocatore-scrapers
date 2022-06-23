import csv
from datetime import datetime

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, Grain_1_KM, SearchableCountries

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


def get_hours(data):
    try:
        hours_of_operation = (
            " Monday "
            + str(
                datetime.strptime(
                    data["opening_time_mon"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_mon"]
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Tuesday "
            + str(
                datetime.strptime(
                    data["opening_time_tue"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_tue"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Wednesday "
            + str(
                datetime.strptime(
                    data["opening_time_wed"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_wed"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Thursday "
            + str(
                datetime.strptime(
                    data["opening_time_thu"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_thu"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Friday "
            + str(
                datetime.strptime(
                    data["opening_time_fri"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_fri"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Saturday "
            + str(
                datetime.strptime(
                    data["opening_time_sat"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_sat"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + ","
            + " Sunday "
            + str(
                datetime.strptime(
                    data["opening_time_sun"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
            + " - "
            + str(
                datetime.strptime(
                    data["closing_time_sun"]
                    .replace("7.:00", "07:00")
                    .replace("8.:00", "08:00")
                    .replace("24:00", "00:00"),
                    "%H:%M",
                ).strftime("%I:%M %p")
            )
        )
    except:
        hours_of_operation = "<MISSING>"

    return hours_of_operation


def fetch_data():
    addresses = []
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }

    max_distance = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_1_KM(),
        max_search_distance_miles=max_distance,
    )

    location_url = "http://hosted.where2getit.com/dollargeneral/rest/locatorsearch?like=0.8201113087423575"

    today_date = datetime.today()

    for zip_code in search:
        data = (
            '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'
            + str(zip_code)
            + '","country":"US","latitude":"","longitude":""}]},"searchradius":"100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        )

        try:
            loc = session.post(location_url, headers=headers, data=data).json()
        except:
            pass

        locator_domain = "https://www.dollargeneral.com/"
        country_code = "US"
        store_number = ""
        location_type = ""
        hours_of_operation = ""

        if "collection" in loc["response"]:
            for data in loc["response"]["collection"]:
                store_number = data["name"].split("#")[-1]

                hours_of_operation = get_hours(data)

                p = store_number.strip()
                page_url = (
                    "http://www2.dollargeneral.com/Savings/Circulars/Pages/index.aspx?store_code="
                    + str(p)
                )
                store = [
                    locator_domain,
                    data["name"],
                    data["address1"],
                    data["city"],
                    data["state"],
                    data["postalcode"],
                    country_code,
                    store_number,
                    data["phone"],
                    location_type,
                    data["latitude"],
                    data["longitude"],
                    hours_of_operation,
                    page_url,
                ]
                search.found_location_at(
                    float(data["latitude"]), float(data["longitude"])
                )
                open_date = datetime.strptime(data["open_date"], "%m-%d-%Y")
                if open_date > today_date:
                    continue
                if store[2] + store[-3] in addresses:
                    continue
                addresses.append(store[2] + store[-3])
                store = [x.strip() if x else "<MISSING>" for x in store]
                yield store

    other_zips = [
        "40108",
        "01702-7133",
        "03055-3127",
        "02136-2833",
        "02301-4849",
        "03060-6303",
        "01826-2928",
        "02368-4173",
        "03051-3707",
        "01852-2623",
        "02122-1321",
        "02141-1018",
        "03054-4131",
        "02150-3723",
        "02151-4309",
        "17238",
        "42743",
        "73860",
        "04920-4038",
        "04493-4349",
        "04928-3738",
        "04765",
        "04401-1403",
        "04947",
        "04419-3556",
        "04468-2190",
        "04461-3614",
        "04444-1904",
        "04927-3601",
        "04428-3219",
        "04496-3414",
        "04955",
        "04901-6007",
        "04963-5378",
        "04294-6646",
        "04974-3311",
        "04915",
        "04952",
        "04254-1529",
        "04330",
        "04351-3407",
        "04253-3653",
        "04664-3112",
        "04862-4431",
        "04259",
        "04786",
        "03585-6213",
        "05846",
        "03574-4710",
        "03584-3138",
        "03598-3095",
        "03582",
        "03282",
        "03581",
        "03223",
        "03217-4544",
        "03254",
        "03222-3573",
        "03886-4533",
        "04037",
        "03814",
        "03276-5015",
        "03220-4519",
        "04047-6215",
        "04289-5105",
        "04281-1620",
        "03303-2108",
        "03809-4624",
        "04048",
        "03303-2074",
        "03307",
        "04049-3509",
        "03225",
        "04061",
        "03851-4641",
        "03234",
        "04350",
        "04240-1907",
        "04578",
        "04282-3754",
        "04250-6020",
        "04543-4660",
        "04240-6100",
        "04210-3955",
        "04039-9431",
        "04062",
        "04106-3659",
        "04106-5517",
        "04093-6505",
        "04064-2605",
        "04002-7708",
        "04090",
        "04027",
        "03906-6724",
        "03903",
        "04622-4406",
        "03861-6629",
        "03077-2656",
        "01930",
        "02330-1110",
        "02538-4803",
        "02601-3651",
        "02673-4844",
        "04785-1008",
        "04750-6300",
        "04736-2154",
        "04694",
        "04666",
        "04654-3412",
        "04652-1203",
        "04643-3432",
    ]

    for zip_code in other_zips:
        data = (
            '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'
            + str(zip_code)
            + '","country":"US","latitude":"","longitude":""}]},"searchradius":"100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        )

        try:
            loc = session.post(location_url, headers=headers, data=data).json()
        except:
            pass

        locator_domain = "https://www.dollargeneral.com/"
        country_code = "US"
        store_number = ""
        location_type = ""
        hours_of_operation = ""

        if "collection" in loc["response"]:
            for data in loc["response"]["collection"]:
                store_number = data["name"].split("#")[-1]

                hours_of_operation = get_hours(data)

                p = store_number.strip()
                page_url = (
                    "http://www2.dollargeneral.com/Savings/Circulars/Pages/index.aspx?store_code="
                    + str(p)
                )
                store = [
                    locator_domain,
                    data["name"],
                    data["address1"],
                    data["city"],
                    data["state"],
                    data["postalcode"],
                    country_code,
                    store_number,
                    data["phone"],
                    location_type,
                    data["latitude"],
                    data["longitude"],
                    hours_of_operation,
                    page_url,
                ]
                open_date = datetime.strptime(data["open_date"], "%m-%d-%Y")
                if open_date > today_date:
                    continue
                if store[2] + store[-3] in addresses:
                    continue
                addresses.append(store[2] + store[-3])
                store = [x.strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
