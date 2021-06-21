import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def get_locations():
    session = SgRequests()
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }

    url = "https://www.google.com/maps/vt?pb=!1m4!1m3!1i6!2i16!3i22!1m4!1m3!1i6!2i16!3i23!1m4!1m3!1i6!2i17!3i22!1m4!1m3!1i6!2i17!3i23!1m4!1m3!1i6!2i18!3i22!1m4!1m3!1i6!2i18!3i23!2m3!1e0!2sm!3i554277016!2m73!1e2!2sspotlight!5i1!8m68!11e11!12m41!1sgood+health+mart+stores!2m2!1s115654710677871163305!2s!3m1!3s0x0%3A0xbfa6359bef5b4108!3m1!3s0x0%3A0x7d0820e022a408b!3m1!3s0x0%3A0xfae7b936f290ed4b!3m1!3s0x0%3A0x9459a2f6f6318a7f!3m1!3s0x0%3A0xb5bca18553b7b58d!3m1!3s0x0%3A0x5624001e452f0557!3m1!3s0x0%3A0x5e0458e55e05bb5b!3m1!3s0x0%3A0xf8477c6768a5c5c4!3m1!3s0x0%3A0xf7b4e87b4a208e21!3m1!3s0x0%3A0x25953cbf9609e566!5sontario!8m6!3m2!3d41.6765559!4d-95.1562271!4m2!3d56.931393!4d-74.3206479!10b0!13m7!1s0x4cce05b25f5113af%3A0x70f8425629621e09!2sgoodhealthmart+stores+ontario!4m2!3d51.253775!4d-85.323214!5e1!6b1!13m14!2shh%2Chplexp%2Ca!14b1!18m7!5b0!6b0!9b1!12b1!16b0!20b1!21b1!22m3!6e2!7e3!8e2!19u6!19u7!19u11!19u12!19u14!19u29!19u37!19u30!19u61!19u70!360939496m0!3m12!2sen!3sIN!5e289!12m4!1e68!2m2!1sset!2sRoadmap!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1&client=google-maps-embed&token=95874"

    r = session.get(url, headers=headers)
    data_json = r.json()

    list_of_ids = []
    location_names_list = []
    for i in data_json:
        try:
            features = i["features"]
            for j in features:
                list_of_ids.append(j["id"])
                data_json_2 = j["c"]
                data_json_2c = json.loads(data_json_2)
                locname = data_json_2c["1"]["title"]
                location_names_list.append(locname)
        except Exception:
            pass
    location_names_list = [locname.replace(" ", "+") for locname in location_names_list]
    locname_and_id = dict(zip(list_of_ids, location_names_list))

    url_gmaps_as_getentitydetails = "https://www.google.com/maps/api/js/ApplicationService.GetEntityDetails?pb=!1m6!1m5!2s"
    url_dimension = "!3m2!1d!2d!4s"
    url_locations = []

    for id_, locname in locname_and_id.items():
        url_store_data = f"{url_gmaps_as_getentitydetails}{locname}{url_dimension}{id_}"
        url_locations.append(url_store_data)

    return url_locations


def fetch_data():
    out = []
    urls = get_locations()
    locator_domain = "https://goodhealthmart.com/"
    session = SgRequests()
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }

    for url in urls:
        r = session.get(url, headers=headers)
        location_name = url.split("!2s")[1].split("!3m2")[0].replace("+", " ")
        d = eval(r.text.split(")]}'\n")[-1].replace("null", '""'))[1]
        if "Good Health Mart" not in str(d):
            continue

        try:
            page_url = d[11][0]
        except IndexError:
            page_url = "<MISSING>"
        latitude, longitude = d[0][2]
        street_address = d[2][0]
        line = d[2][1].replace("Ontario", "Ontario, ON ")

        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.replace(state, "").strip()
        country_code = "CA"
        store_number = "<MISSING>"
        phone = d[7]
        location_type = "<MISSING>"

        _tmp = []
        try:
            for i in d[-1][0]:
                day = i[0]
                time = i[3][0][0]
                _tmp.append(f"{day}: {time}")
        except:
            pass

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
