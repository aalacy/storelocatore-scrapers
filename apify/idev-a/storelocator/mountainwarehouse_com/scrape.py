import csv
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.mountainwarehouse.com"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "content-length": "60",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": '__cfduid=d275eafe8307e26651284576cc5541fd61612514477; MW.ANONYMOUSUSER=8KnKcQpfijfm462LQGPrhQl1zBCsVirdlnV4liIUodtH1ZIX_vJygEiOsJMNI-9IfEfr4aKUf-XowMD336MPAbeS8O-1wFId5WeYHKwQHyTuNppf8lby2xskxG-4WoX4YUpdFa5pAyRghOoBFFDl-Q2; mw_culture=en-GB; mw_session_created=; RES_TRACKINGID=428980583051489; ResonanceSegment=1; _gcl_au=1.1.1966789761.1612514513; recordID=1243b7d5-e570-4dae-ad0c-92d09dc2ee9a; _ga=GA1.2.941014072.1612514530; _gid=GA1.2.1566249153.1612514530; rmStore=dmid:1545; MW_CFSPOPUP=true; SSID=CACoMh0AAAAAAACuBB1gxXCBA64EHWACAAAAAAAAAAAAn7kdYACE1Q; SSSC=729.G6925696947395326149.2|0.0; SSRT=n7kdYAQBAA; dmSessionID=7645e5fa-fa8a-4093-9318-622bd96a6018; _dc_gtm_UA-5203215-1=1; _uetsid=089fb140678e11eb9a73dd87266fb091; _uetvid=089fefd0678e11eba82cf544a177b43b; stc114568=env:1612560804%7C20210308213324%7C20210205220403%7C3%7C1039983:20220205213403|uid:1612514531964.1341246953.3320804.114568.1828737096:20220205213403|srchist:1039983%3A1612560804%3A20210308213324:20220205213403|tsa:1612560804195.1521337619.7602172.7055640384724535.:20210205220403; S2Sv4={"S2SID":"000002210205084246489520210205213315","S2PGS":"3","S2HE":"0","S2CU":"0","S2FS":"0","S2SDPPG":"3|89|1|0|0|-1","S2SDPDI":"3|11|10|0|0|-1","LU":"202102051634"}; V1v4={"V1":"22102050842464895","V3":"0","S2S":{"S2SID":"000002210205084246489520210205213315","S2PGS":"3","S2HE":"0","S2CU":"0","S2FS":"0","S2SDPPG":"3|89|1|0|0|-1","S2SDPDI":"3|11|10|0|0|-1","LU":"202102051634"}}',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    data = {
        "SearchTerm": "LA22 9BT",
        "Latitude": "54.4320757",
        "Longitude": "-2.9629846",
    }
    res = session.post(
        "https://www.mountainwarehouse.com/stores/results/",
        headers=headers,
        data=data,
    )
    store_list = json.loads(
        res.text.split("App.Components.StoreResults, ")[1].split("), ")[0]
    )["AllStores"]
    data = []
    for store in store_list:
        country_code = store["CountryCode"]
        if country_code != "GB":
            continue
        location_name = store["StoreName"]
        page_url = (
            "https://www.mountainwarehouse.com/stores/"
            + store["BranchCode"]
            + "/"
            + store["StoreName"].replace(" ", "-")
        )
        phone = store["Phone"]
        city = store["City"] or "<MISSING>"
        zip = store["PostCode"]
        state = store["Province"] or "<MISSING>"
        street_address = (store["Address1"] or "") + " " + (store["Address2"] or "")
        street_address = street_address.strip()
        store_number = store["store_id"] if "store_id" in store.keys() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store["Lat"]
        longitude = store["Long"]
        hours_of_operation = ""
        for x in store["OpeningHours"]:
            hours_of_operation += (
                x["DayName"]
                + ": "
                + (
                    "Closed"
                    if x["OpenTime"] == "Closed"
                    else x["OpenTime"] + "-" + x["CloseTime"]
                )
                + " "
            )
        hours_of_operation = hours_of_operation.strip()
        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                '="' + phone + '"',
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


if __name__ == "__main__":
    scrape()
