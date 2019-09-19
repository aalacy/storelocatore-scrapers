import json

import requests
import sgzip
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.oakley.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        countries = []
        seen = []
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        for zipcode_search in sgzip.for_radius(125):
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
                "cookie": "aka-cc=US; mt.v=2.1989181814.1567440816920; tracker_device=4544e626-732d-4e11-b01f-804a065ae372; osi18=ya; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; s_cc=true; _ga=GA1.2.2020812089.1567440870; _gcl_au=1.1.2074907376.1567440870; cto_lwid=bf4b69f3-3a71-4180-b6d2-f2e9ba231818; WRUIDAWS20180402=2414517833138388; _fbp=fb.1.1567440873432.1634903518; s_sq=%5B%5BB%5D%5D; aka-ct=REDWOODCITY; aka-zp=94061-94065; ak_bmsc=06D0A367FF7499501A92873D0F53BE54B81BB3BA1E2700007972765D2BC98715~plhZtDWJDlXm/icGfJGx8a+ghoGRkWCNniqcv/ttDfhqsGZVuDmNPYWHu747HA0bXWMePs24eyrIoecV4oy6kXQsFxRFlv6rte22S/P7lF3DgNE41nLRaxY2gLE1zz2CJply+IM1nwOMP5/pLyaoOSCYZy6MRABoTTv8JLvhPm1chWAZxON5KYcx5Y26MrBtFvzGwV2dbihvpBM+x8rXfIXiUR/Yf/sHMc/4JgZJb9vKWYhmH36aqwFxeeaYaORyU0; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18149%7CMCMID%7C47422393290484898843689179922376543218%7CMCAAMLH-1568648444%7C9%7CMCAAMB-1568648444%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1568050844s%7CNONE%7CMCAID%7C2E9C880705035FDF-40001195400002FE%7CvVersion%7C3.3.0; _gid=GA1.2.1691496386.1568043644; _CT_RS_=Recording; SECSESSIONID=a0e070370bbf7e25a34455b059eac93ff7a823d4; JSESSIONID=9815D21F5DC6A8850421D4EDE60FBBD4.app19; bounceClientVisit2511v=N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgO6kB0A9gIYDWYApgJ5kDGFAtkfQHYC0ArihAAaEACcYIEAF8gA; User_Status=anonymous|Guest; _4c_=LY1bbsQwCEX3wncagQ2YZDeJTdSq1XQ0HfUVee%2BDq%2FLDReKec8LXs19gJVFDVkQWxQle%2FecD1hNuL22sT1iB6TBJubjkYo1lywfW1NrurO5SYYLvwSmSqGQzJewT1Ot%2F%2F4T63jw4tMw6a3zff%2BN64oSR%2FTIU11uLfEQFMhOjslA13TY8LO2NvRoW37mSQrD%2FdGqUU%2BaFFwnk%2FQ1WU8YxvfcH; utag_main=v_id:016cf2c1592e00ab0cc2a4be749803079001c0710093c$_sn:5$_ss:0$_st:1568047805933$vapi_domain:oakley.com$ses_id:1568045937151%3Bexp-session$_pn:3%3Bexp-session; criteo_write_test=ChUIBBINbXlHb29nbGVSdGJJZBgBIAE; ctm={'pgv':385209164724913|'vst':7109241815390945|'vstr':7152257511565319|'intr':1568046006071|'v':1|'lvst':35}; _gat_tealium_0=1; bm_sv=D989D9B94AB5EF505258646AF0895833~6+VvL1yAdVDj26RUJ4GNJpNY9fwyXrGLR59l4VBnOPArsvxgwp4EQ50f63mtvJasJjmvYxqD2+hLiYYIfH5xKyT1gOsEJTNZ8PrVgHBDfURb9jAgBCT18x+ecg9/AbNmnNi/sKxOxYGTwD6Hpt0+B99O2Fjh+Oh35jIwB1r5A7E=; __CT_Data=gpv=12&ckp=tld&dm=oakley.com&apv_14_www46=12&cpv_14_www46=12&rpv_14_www46=12",
                "dnt": "1",
                "referer": f"https://www.oakley.com/en-us/store-finder?q={zipcode_search}",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }

            r = requests.get(
                f"https://www.oakley.com/en-us/store-finder/stores?q={zipcode_search}&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on&_requestConfirmationToken=6bcdb8fb-63a4-46fc-87bc-cda74d68f260",
                headers=headers,
            )

            stores.extend(json.loads(r.content)["stores"])

            for store in stores:
                # Name
                location_title = store["name"]

                # Store ID
                location_id = store["id"]

                # Street Address
                street_address = (
                    store["addressMap"]["streetAddress"]
                    if "streetAddress" in store["addressMap"].keys()
                    else "<MISSING>"
                )

                # City
                city = (
                    store["addressMap"]["addressLocality"]
                    if "addressLocality" in store["addressMap"].keys()
                    else "<MISSING>"
                )

                # State
                state = (
                    store["addressMap"]["addressRegion"]
                    if "addressRegion" in store["addressMap"].keys()
                    else "<MISSING>"
                )

                # Zip
                zip_code = (
                    store["addressMap"]["postalCode"]
                    if "postalCode" in store["addressMap"].keys()
                    else "<MISSING>"
                )

                # Hours
                hour = store["hoursMap"] if store["hoursMap"] != {} else "<MISSING>"

                # Lat
                lat = store["lat"]

                # Lon
                lon = store["lng"]

                # Phone
                phone = store["phone"]

                # Country
                country = (
                    store["addressMap"]["addressCountry"]
                    if "addressCountry" in store["addressMap"].keys()
                    else "<MISSING>"
                )

                # Store data
                locations_ids.append(location_id)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                states.append(state)
                zip_codes.append(zip_code)
                hours.append(hour)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                cities.append(city)
                countries.append(country)

        for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            latitude,
            longitude,
            hour,
            location_id,
            country,
        ) in zip(
            locations_titles,
            street_addresses,
            cities,
            states,
            zip_codes,
            phone_numbers,
            latitude_list,
            longitude_list,
            hours,
            locations_ids,
            countries,
        ):
            if location_id not in seen:
                self.data.append(
                    [
                        self.url,
                        locations_title,
                        street_address,
                        city,
                        state,
                        zipcode,
                        country,
                        location_id,
                        phone_number,
                        "<MISSING>",
                        latitude,
                        longitude,
                        hour,
                    ]
                )
                seen.append(location_id)

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
