import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="picknsave.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    session = SgRequests()

    api_link = "https://www.picknsave.com/stores/api/graphql"

    data = []
    found_poi = []

    max_results = 50
    max_distance = 100

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Searching items..Appr. 10mins..")

    for zipcode in search:

        json = {
            "query": "\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n",
            "variables": {"searchText": zipcode, "filters": []},
            "operationName": "storeSearch",
        }

        headers = {
            "authority": "www.picknsave.com",
            "method": "POST",
            "path": "/stores/api/graphql",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-length": "1039",
            "content-type": "application/json;charset=UTF-8",
            "cookie": 'bm_sz=D2B95028FB5BE8BF15BD92F54C7609E7~YAAQnf4wF8yqO0V2AQAA9ujgYwqJO1EwQfj2QV99OUQW8NUzvR4n4dXAWs1Er5qD9RJhn5Xu/qVslZPFqOYUhtWW4gDd1atez6rOCp4DfXxlS+Q2Azj7Grh1w+qYva4bUU1THNPwNI/3rxF1A1t3s46F3VSKICII3AYGt2tv54OpE6GX57Rwn7g+/aDg8F3fkkx8; pid=68b487d0-44ce-46e8-a126-b9a050003988; origin=fldc; x-active-modality={"type":"PICKUP","locationId":"53400353"}; sid=e1a7d3ce-e0d5-5725-4dfa-6016dac6fece; akacd_RWASP-default-phased-release=3785446252~rv=61~id=c8d2d58e65aa9eefc72028393cbc58f7; rxVisitor=160799345413667KP5HR5MQ2EU4K186PSEL8ODSUQJG1S; dtSa=-; AMCVS_371C27E253DB0F910A490D4E%40AdobeOrg=1; s_cc=true; _gcl_au=1.1.1302758771.1607993460; dtCookie=40$A65B10C4DB2668212EEC89E2EDEDD2DC|81222ad3b2deb1ef|1; _pin_unauth=dWlkPVpUazJPR0V4WW1VdFpHVTVZeTAwTW1JMUxUazJZVEF0WkRCaU1EQTVZVEV4TWpGag; akaalb_KT_Digital_BannerSites=~op=KT_Digital_BannerSites_GCP_Search_Central1:gcpsearchcentral1|KT_Digital_BannerSites_KCVG_CDC_FailoverHDC:cdc|~rv=19~m=gcpsearchcentral1:0|cdc:0|~os=49d9e32c4b6129ccff2e66f9d0390271~id=8a26c5accd73d5f70f6f1fd150efd8ac; _krgrtst=01fbdea9%3Bd7930f7f; abTest=tl_dyn-pos_A|mrrobot_12b59e_B; AKA_A2=A; ak_bmsc=8A9B701804740D0282D7B4143EF15C341730FE9DD40700002032D85F98FA5008~pl6CCNZlcW/tIFlN1MdlMvFNH8a5L80HaP+dzOeFwll3sfGUJiJ2mkvPUxRj6aHSLG9p/WowGumJq8jOTbp1qBqty3rJUcnXXk09ZB73LcBaeUQptbORZyBBsXxfTYJvf2OUrHIDw9xkMMdHWI8wMddgCi3ZzSMC2+20jsOx4jY85anQ/ou34B0MWwDTr5GR8MYbABo+/3XIYSnvbGS3GTfB5pkIH28pU+gfcX7+K3OHFCozI2/J0/mc0CM1Q3utrR; AMCV_371C27E253DB0F910A490D4E%40AdobeOrg=-432600572%7CMCIDTS%7C18612%7CMCMID%7C07964017235293848852972655609128842536%7CMCAAMLH-1608608935%7C7%7CMCAAMB-1608608935%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1608011335s%7CNONE%7CMCAID%7C2FEC043885159007-4000088F993D7A39%7CvVersion%7C4.5.2; RT="z=1&dm=picknsave.com&si=noupf5ya0rr&ss=kipawffl&sl=0&tt=0"; __VCAP_ID__=bc54f6a0-eb12-402a-55c4-83f5; s_tp=1223; s_tslv=1608004477000; s_ips=473; _uetsid=98d368103e6f11ebac3ea1e0766010a9; _uetvid=98d3ac103e6f11eba020998d12d61b73; s_ppv=bn%253Astores%253Asearch%2C55%2C39%2C675%2C1%2C2; bm_sv=FEBE5EB06193B9707D81757846D22276~myKjipRNMUMQtz9iyFwAtdgpso9MYjOq5GKufd0ydGua8+fMVw9Lf2KI8cqrGjcWGjtsPG0rI27UdWFLsHwevi8Y4nLy9gx0udmP/WxxqZ/zjTs+qpY1Paqdezcjg8lme5cIMZx7RCBGI13+aPqmHAhyE1zYqF6tQIbK5c5b9Jg=; dtLatC=3; s_sq=krgrmobileprod%3D%2526pid%253Dbn%25253Astores%25253Asearch%2526pidt%253D1%2526oid%253Dfunctioncn%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DSUBMIT; _abck=D6FC26ADF93BF821DA6E4FDE876B6730~-1~YAAQnf4wF5mPP0V2AQAA7mCJZAU7fJe382vgFHHkFS2unJzVFRyIueHfRMuMnx3KlRAeEfxJJXEdUTmwstnMljBNDoK7CBCsI0mQHSYtJPNfP7O3zNvpNtmMdC6SyGXNe3/p8sfw50BOX7BRmac1XuXiUYyavEpbNTxS0b0KJ9vf+vMyKXzdC36CFAfhGrjiy0eeECinWguUoq0OxLKag1LTZaGPkTl0TxGLguvYsp5vMl895w3BsFwfCWrSIe5EIhkmXA9Idl2q/7Vg8h/aHxnw4i6ddoMCMxymMi6TDOK3wPdpRJOr0oKqVU/9nPd9MdrfqFBTl5c1L0CfdqvEGzhyvEaNkF7E2nf9LtzR+0mFBUf9QK8=~-1~-1~-1; rxvt=1608006293726|1608003649611; dtPC=40$4388357_768h44vFKQDKMLIBBHRLIRFMWWOFODFRPKBDPER-0e12',
            "origin": "https://www.picknsave.com",
            "referer": "https://www.picknsave.com/stores/search?searchText=" + zipcode,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
            "x-dtpc": "40$4388357_768h44vFKQDKMLIBBHRLIRFMWWOFODFRPKBDPER-0e12",
            "x-dtreferer": "https://www.picknsave.com/stores/search",
        }

        store_data = session.post(api_link, headers=headers, json=json).json()["data"][
            "storeSearch"
        ]["stores"]
        fuel_data = session.post(api_link, headers=headers, json=json).json()["data"][
            "storeSearch"
        ]["fuel"]

        locator_domain = "picknsave.com"

        for store in store_data:
            store_number = store["storeNumber"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)

            link = "https://www.picknsave.com/stores/details/%s/%s" % (
                store["divisionNumber"],
                store_number,
            )
            location_name = store["vanityName"]
            try:
                street_address = (
                    store["address"]["addressLine1"]
                    + " "
                    + store["address"]["addressLine2"]
                ).strip()
            except:
                street_address = store["address"]["addressLine1"].strip()
            city = store["address"]["city"]
            state = store["address"]["stateCode"]
            zip_code = store["address"]["zip"]
            country_code = "US"
            location_type = "Store"

            phone = store["phoneNumber"]
            if not phone:
                phone = "<MISSING>"

            hours_of_operation = ""
            raw_hours = store["ungroupedFormattedHours"]
            for hours in raw_hours:
                day = hours["displayName"]
                opens = day + " " + hours["displayHours"]
                hours_of_operation = (hours_of_operation + " " + opens).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.mark_found([latitude, longitude])

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

        for store in fuel_data:
            store_number = store["storeNumber"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)

            link = "https://www.picknsave.com/stores/details/%s/%s" % (
                store["divisionNumber"],
                store_number,
            )
            location_name = store["vanityName"]
            try:
                street_address = (
                    store["address"]["addressLine1"]
                    + " "
                    + store["address"]["addressLine2"]
                ).strip()
            except:
                street_address = store["address"]["addressLine1"].strip()
            city = store["address"]["city"]
            state = store["address"]["stateCode"]
            zip_code = store["address"]["zip"]
            country_code = "US"
            location_type = "Fuel"

            phone = store["phoneNumber"]
            if not phone:
                phone = "<MISSING>"

            hours_of_operation = ""
            raw_hours = store["ungroupedFormattedHours"]
            for hours in raw_hours:
                day = hours["displayName"]
                opens = day + " " + hours["displayHours"]
                hours_of_operation = (hours_of_operation + " " + opens).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.mark_found([latitude, longitude])

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
