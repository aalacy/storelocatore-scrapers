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
        "s_vi": "[CS]v1|3034E589F059B8AC-4000198793A3DF36[CE]",
        "rxVisitor": "1621520236497Q19NCI2KOQPF4L2VS9LNB5TOJQ6D6IR2",
        "sgh-desktop-facet-state-search": "",
        "JSESSIONID": "0000VrOYtzuK_6S7wOxVAUqF426:1c7qtp224",
        "ak_bmsc": "349C859658EE2EA6905EB0C1D2140013021555AFEA6C0000696FA660B2E78716~plcghQy7JbdriQ4PoIhlWw68ostXRMizjRqPQiCz2H2oWvp7KebWzGh5SSZNdFGZRMWOWWWoxzxwhIUfyIbC2xY4bmwPoSaIB/qPy61LGy/S2RepF+XqosV1RV5c7pF+SeM2uP7SIQzd0W6UpKdiffKp1ORJsT+5/kwiDIBC+u43TWWcthpXtFI/csrAIac/cbxpzRViek4No0G6zdaVi1/F5SQyFyrzoBEAmmDWR7R1WooxnmpW7DO/QkMWgRiFPZ",
        "tealium_data_session_timeStamp": "1621520241337",
        "userToken": "undefined",
        "AMCVS_125138B3527845350A490D4C%40AdobeOrg": "1",
        "AMCV_125138B3527845350A490D4C%40AdobeOrg": "-1303530583%7CMCIDTS%7C18768%7CMCMID%7C31837677145346142053689448579183674801%7CMCAAMLH-1622125041%7C3%7CMCAAMB-1622125041%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1621527441s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0",
        "_cs_mk": "0.7991072550211658_1621520242394",
        "s_cc": "true",
        "__wid": "180405334",
        "dtCookie": "v_4_srv_5_sn_ILDOQQQSJ75UEADO1EO86V9HNQHAPRDQ_app-3Ab359c07662f0b428_1_ol_0_perc_100000_mul_1",
        "__utma": "110589831.458204620.1612788211.1617545831.1621520245.16",
        "__utmc": "110589831",
        "__utmt": "1",
        "dtSa": "true%7CC%7C-1%7CFIND%20A%20STORE%7C-%7C1621520249074%7C320236466_42%7Chttps%3A%2F%2Fwww.sunglasshut.com%2F%7CSunglass%20Hut%C2%AE%20Online%20Store%20%5Ep%20Sunglasses%20for%20Women%5Ec%20Men%20%26%20Kids%7C1621520244110%7C%7C%7C%2F%7C1621520232839",
        "WRIgnore": "true",
        "WC_SESSION_ESTABLISHED": "true",
        "WC_AUTHENTICATION_-1002": "-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D",
        "SGPF": "3LgqVeXDO41XQ3zUHqg7qcRnpTy5up0f-Fuqp99NDR9Y_q2IPdTUJOA",
        "_gid": "GA1.2.2041786321.1621520270",
        "_sctr": "1|1621450800000",
        "amp_f24a38": "otxvCgA0M7d8OZIu1lIv6c..1.1f6526eri.1f652853m.0.0.0",
        "MGX_UC": "JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyMWJjNDM0NmItODIzNS00NTU2LTg2YzItNThlZmRmYjEwOWQyJTIyJTJDJTIyZSUyMiUzQTE2MjIwNDU4OTU5MzYlN0QlMkMlMjJNR1hfUFglMjIlM0ElN0IlMjJ2JTIyJTNBJTIyNjVlMDI1ZjQtODQ2NS00NTA5LTg0OTUtOWQ3NmVjYzIyYWQ2JTIyJTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTYyMTUyMjA5ODEwMCU3RCUyQyUyMk1HWF9DSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyMDIzOTE4MTItZWQzOS00NDFiLWE3NjItYzI0ZDExYWY1YjA1JTIyJTJDJTIyZSUyMiUzQTE2MjIwNDU4OTU5NDUlN0QlMkMlMjJNR1hfVlMlMjIlM0ElN0IlMjJ2JTIyJTNBNCUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2MjE1MjIwOTgxMDAlN0QlMkMlMjJNR1hfRUlEJTIyJTNBJTdCJTIydiUyMiUzQSUyMm5zX3NlZ18wMDAlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjIxNTIyMDk4MTAwJTdEJTdE",
        "_derived_epik": "dj0yJnU9V3h2R2hKbkY2UzY3RXlVb2tzV3hBWVFCLVRYVDd0eUombj1SZEhNLTl3VFRPRTJ1X3VtMmdnUl93Jm09ZiZ0PUFBQUFBR0NtYjZrJnJtPWYmcnQ9QUFBQUFHQ21iNms",
        "outbrain_cid_fetch": "true",
        "WC_PERSISTENT": "OtX0myJhoEu0Ct4H%2Be2Y9bP6G5QTkDoHV7jh3gqwQaI%3D%3B2021-05-20+14%3A18%3A30.078_1621520250665-12657_11352_-1002%2C-24%2CGBP_10152_-1002%2C-1%2CUSD_11352",
        "WC_ACTIVEPOINTER": "-24%2C11352",
        "TS011f624f": "015966d292060741251562055a6f950b33cb0df530454eca2a7cf3243d7fb569ba9842bc541248216daec04a8c98a19df5de40f90748e0550871ec7e33a7ac1786c8510ce11ee7e67a041bf4061ada7b5b3509b8d0b2f9aed1a93524691d5ac7dcb3d43581b9f26b846ca5958252c8db9b7320aa60c7f9e43b347a6b4e79614b3621eb6de1614c192b888e0023e2c3ec506a3e0d938c74aea38e62c6af0431e61fb8331f477bae8d052ed8622c715ad2265400fdbe",
        "_cs_cvars": "%7B%221%22%3A%5B%22Page%20Type%22%2C%22Clp%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22%3AClp%22%5D%2C%223%22%3A%5B%22Page%20Section%201%22%2C%22Home%22%5D%2C%224%22%3A%5B%22Action%22%2C%22GB%3AEN%3AD%3A%3AClp%20%22%5D%2C%228%22%3A%5B%22User%20Login%20Status%22%2C%22Guest%22%5D%7D",
        "_cs_id": "f413445d-a8fc-ab37-e274-a45cad2ecd76.1612788228.26.1621520320.1621520248.1.1646952228991.Lax.0",
        "_cs_s": "6.1",
        "__CT_Data": "gpv=50&ckp=tld&dm=sunglasshut.com&apv_358_www06=45&cpv_358_www06=45&rpv_358_www06=9&apv_283_www06=8&cpv_283_www06=8&rpv_283_www06=4",
        "smc_session_id": "4JOjWaAK8PHT7rthx78eAO2GmSWxAvIP",
        "smc_spv": "1",
        "smc_tpv": "43",
        "smc_sesn": "5",
        "smct_session": '{"s":1621520322595,"l":1621520331605,"lt":1621520331607,"t":9,"p":7}',
        "cookiePolicy": "true",
        "dtLatC": "134",
        "rxvt": "1621522134911|1621520236505",
        "sgh-desktop-facet-state-plp": "categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false",
        "bm_sv": "4DED9EB495612FD9C3335C907777F269~0SEbUnoXeeHjHvmEvdej6veo1rifaf5uH21oah8vG6xG8nA28K1eIpqElAMRX87eZOLgtO7W880gMgU/RROuXj0JFbgDpZwoqIQiO4IDrr9e6bcdamC0+op4UbMPthkAkE3TNv26p1ez/F/gkP7jYxiIBgXSBmQr5cyz4L4nFCw=",
        "s_sq": "%5B%5BB%5D%5D",
        "__utmb": "110589831.9.10.1621520245",
        "_uetsid": "1a4c5020b97611eb918efdad97a1be35",
        "_uetvid": "1a4de840b97611ebab917bf83e7542b8",
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
                if latitude == "" or latitude == "0.00000":
                    latitude = "<MISSING>"
                if longitude == "" or longitude == "0.00000":
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
