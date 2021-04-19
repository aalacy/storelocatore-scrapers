# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import json

website = "sunglasshut.com/uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []
    search = static_coordinate_list(
        radius=100, country_code=SearchableCountries.BRITAIN
    )
    cookies = {
        "mt.v": "2.765874924.1612788200341",
        "ftr_ncd": "6",
        "s_ecid": "MCMID%7C31837677145346142053689448579183674801",
        "CONSENTMGR": "consent:true%7Cts:1612788210096",
        "_scid": "2e7e007d-1be5-4c30-9f88-b35b9318763e",
        "__utmz": "110589831.1612788211.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "_cs_c": "1",
        "_gcl_au": "1.1.205447344.1612788226",
        "WRUIDAWS": "3157488901570697",
        "smc_uid": "1612788231161927",
        "smc_tag": "eyJpZCI6Njc4LCJuYW1lIjoic3VuZ2xhc3NodXQuY29tIn0=",
        "smc_refresh": "13169",
        "smc_not": "default",
        "_ga": "GA1.2.458204620.1612788211",
        "BVBRANDID": "e4520975-41c8-4088-8159-4a1205dafe36",
        "_pin_unauth": "dWlkPU5EaG1NelUzT0RFdE1XRmpPUzAwT1RBeUxXSTJaV1V0TmpaaFpEVmhNV1V4TlRReQ",
        "_derived_epik": "dj0yJnU9ZmFoc3lOa1U0QU0wXzd6R3Uwa29NRmRGTUstbWktU2Qmbj1vQVE3M2lyUzkwMzg0VFpVbUVfa3dBJm09ZiZ0PUFBQUFBR0FuNnlZJnJtPWYmcnQ9QUFBQUFHQW42eVk",
        "MGX_UC": "JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyNTc4NDkyYTMtZDdjZC00NzY2LTk5MWUtNzZkYzM4MzZiZTljJTIyJTJDJTIyZSUyMiUzQTE2MTM3NTQ0MzgwMTIlN0QlMkMlMjJNR1hfVSUyMiUzQSU3QiUyMnYlMjIlM0ElMjJmY2RkODRlZi03ZmU3LTRmNDMtYTdkOC0yMzc2ZDVmYTAwMDklMjIlMkMlMjJlJTIyJTNBMTYxMzc1NDQzODAyMCU3RCUyQyUyMk1HWF9QWCUyMiUzQSU3QiUyMnYlMjIlM0ElMjJjMjgwMGZmMi1lNGJmLTQ2ZTMtODVkYy03ZDE5ZWI2MGQyMDMlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjEzMjMwNjM4NzcyJTdEJTJDJTIyTUdYX0NJRCUyMiUzQSU3QiUyMnYlMjIlM0ElMjJmYTEyOWJkOC0yZTNiLTQ1NzYtOGViYS03MDM1YjQyMzRjYjYlMjIlMkMlMjJlJTIyJTNBMTYxMzc1NDQzODAyOCU3RCUyQyUyMk1HWF9WUyUyMiUzQSU3QiUyMnYlMjIlM0E0JTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTYxMzIzMDYzODc3MiU3RCUyQyUyMk1HWF9FSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIybnNfc2VnXzAwMCUyMiUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2MTMyMzA2Mzg3NzIlN0QlN0Q=",
        "SGPF": "3FzfxAgVHXUy3QyzfhDap3jaV0KL5ZBRIGSy91xyOmz8mTSa0ZJcbIA",
        "_sctr": "1|1617130800000",
        "aka-zp": "",
        "JSESSIONID": "0000JINsVWl-PIh03HhBEbfDMe_:1c80pfc7n",
        "WC_SESSION_ESTABLISHED": "true",
        "WC_PERSISTENT": "muQZk2VzSt87tpWtgZ1InbcgHIFTYfxhhLedOjIXYRQ%3D%3B2021-04-04+14%3A16%3A19.135_1612788197221-654745_11352_1449436418%2C-24%2CGBP_10154_1448415594%2C-25%2CCAD_10152_-1002%2C-1%2CUSD_11352",
        "WC_AUTHENTICATION_1449436418": "1449436418%2CkiiowOgo8%2BPEFgKf8G9GeUWkKm6Pmns94q8EC3dIVEc%3D",
        "WC_ACTIVEPOINTER": "-24%2C11352",
        "WC_USERACTIVITY_1449436418": "1449436418%2C11352%2Cnull%2Cnull%2C1617545779138%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C598282317%2CPf0YfT%2FpQ9hIyr5YElL299b97RW73mjM6CKHuUa7JPZ5XBzHNKQKXCFDl39K7Gq3skENq7a7ZyIT6%2FO05to%2FgR%2F8XfBiIkdZts8%2FAhELSjDKaA0VPwD0nPaJ5KMTIgh7Zb1PNKp4Dg1lUwIZAk0V3w%2FxrN6lv3gM4JN6uZIMxMUUIJZCuRkt0bG27wgtMXsi%2B2fI4kUgZhW6z26TX8mgJI8aNqSHn8zVeLKcUNJhE%2FB9JkOZJ5bZKLYu2o1h%2BYBp1D%2FCbrB8f4%2Fo5FKFSrI%2Flg%3D%3D",
        "TS011f624f": "015966d2924901a12e05613048a8b2f39476531e5a8275498b9bbc24bb4c72fe98ae473c8b31eb19cb9ba8c5efc26c2086c06f4673d55af713c90e2e90949954d38bc5ffac11e7c98f8153cce584a9624c96ba24d0d1e0d7ad1873559733964e76aebcf9feaed152ba07530af375f10d52bef7ecd239b86894db3b815004514ad6c72a8797dea622831e89cb7e9b6f0cc3342f8dc6",
        "rxVisitor": "1617545794708VD76UUIVNK8PHLAUSD8NR6TS1IERQ0HG",
        "sgh-desktop-facet-state-search": "",
        "dtCookie": "v_4_srv_1_sn_MQ1RBL4F8TN681TU233RU8QMFO91NTKJ_app-3Ab359c07662f0b428_1_ol_0_perc_100000_mul_1",
        "ak_bmsc": "4A7CCC3177643CABCF8E9F2DE43A1D3617CB3F37D267000035CA69603CC0C255~pldM+qku0sh12OeVvVGspEjjAlj+3y8CdGLhSKeVNs1/d3aUcEXs8evcwJKvTxn1iNtuKeeeJLOi6Nm0MCW6H/9nBPrL12hFANqhUzfCchCU9OKA2yKBd3oT9OGXSzCTuBHnBHWNchSEburJGPigtDpuZoAJCVZCZsHuKsydvBX9/I4jzGFWXmz2vjJK8U+TLLFktj9hUh09NHpHpSJxbE15/uoHYelGMK5DUYbtTdvpxvM7lw3NMaRdTYoHSNN8wV",
        "tealium_data_session_timeStamp": "1617545829150",
        "userToken": "undefined",
        "AMCVS_125138B3527845350A490D4C%40AdobeOrg": "1",
        "AMCV_125138B3527845350A490D4C%40AdobeOrg": "-1303530583%7CMCIDTS%7C18722%7CMCMID%7C31837677145346142053689448579183674801%7CMCAAMLH-1618150630%7C3%7CMCAAMB-1618150630%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1617553030s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0",
        "_cs_mk": "0.804171746331696_1617545830838",
        "s_cc": "true",
        "__utma": "110589831.458204620.1612788211.1617196181.1617545831.15",
        "__utmc": "110589831",
        "__utmt": "1",
        "_cs_cvars": "%7B%221%22%3A%5B%22Page%20Type%22%2C%22Clp%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22%3AClp%22%5D%2C%224%22%3A%5B%22Action%22%2C%22GB%3AEN%3AD%3A%3AClp%20%22%5D%2C%228%22%3A%5B%22User%20Login%20Status%22%2C%22Guest%22%5D%7D",
        "_cs_id": "f413445d-a8fc-ab37-e274-a45cad2ecd76.1612788228.25.1617545836.1617545836.1.1646952228991.Lax.0",
        "_cs_s": "1.1",
        "__CT_Data": "gpv=42&ckp=tld&dm=sunglasshut.com&apv_358_www06=41&cpv_358_www06=41&rpv_358_www06=9&apv_283_www06=4&cpv_283_www06=4&rpv_283_www06=4",
        "smc_session_id": "L2SIEBmoRsVFDiZw9skHRhOkOHUDrmSq",
        "smc_spv": "1",
        "smc_tpv": "39",
        "smc_sesn": "4",
        "smct_session": '{"s":1617545838220,"l":1617545856222,"lt":1617545855226,"t":17,"p":16}',
        "cookiePolicy": "true",
        "dtSa": "-",
        "dtLatC": "20",
        "rxvt": "1617547659675|1617545794715",
        "sgh-desktop-facet-state-plp": "categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false",
        "s_sq": "%5B%5BB%5D%5D",
        "bm_sv": "333722F88433AA39AAD0CF96B528B81C~DodLEapej2uKv3r9HjcjBIVToqdF88nA1QdyuDPsEeCJnxNdORkel44ed5BBy79RSRIyZ+Tby/7Pvt8IsjSDdZ2F9x8WAnPnZIdfZ2+qeIlLA1pjavRrGKKdSY1vM5DEhbdg2gqWn+a2iMKVb7ddD2eSkPzaPbiA6CDF54ATQMY=",
        "__utmb": "110589831.2.10.1617545831",
        "_uetsid": "7e20f650955011ebbc8011b3ba704d1f",
        "_uetvid": "1e72d4c0827511ebb0c2338728deaa80",
        "forterToken": "ef237a866745434883cb62b601ec1bf0_1617545860213_217_UDF4_6",
    }

    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=Manchester%2C%20UK",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    store_id_list = []
    for lat, long in search:
        log.info(f"{(lat, long)}")

        params = (
            ("latitude", lat),
            ("longitude", long),
            ("radius", "2000"),
        )

        stores_req = session.get(
            "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations",
            headers=headers,
            params=params,
            cookies=cookies,
        )

        stores = json.loads(stores_req.text)["locationDetails"]
        for store in stores:
            if store["countryCode"] == "GB":
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["displayAddress"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store["address"]

                city = store["city"]
                state = "<MISSING>"
                zip = store["zip"]
                country_code = store["countryCode"]

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                phone = store["phone"]
                location_type = "<MISSING>"

                store_number = store["id"]
                if store_number in store_id_list:
                    continue
                store_id_list.append(store_number)
                hours = store["hours"]
                hours_list = []
                for hour in hours:
                    day = hour["day"]
                    time = ""
                    if len(hour["open"]) <= 0 and len(hour["close"]) <= 0:
                        time = "Closed"
                    else:
                        time = hour["open"] + "-" + hour["close"]

                    hours_list.append(day + ":" + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

                latitude = store["latitude"]
                longitude = store["longitude"]
                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

                curr_list = [
                    locator_domain,
                    page_url,
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
                ]
                loc_list.append(curr_list)
        #         break
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
