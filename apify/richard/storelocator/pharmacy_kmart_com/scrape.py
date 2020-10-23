import requests
import sgzip
from Scraper import Scrape
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pharmacy_kmart_com')



URL = "https://pharmacy.kmart.com"


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
        stores = []
        page_urls = []
        seen = []

        cookies = {
            "$Cookie: JSESSIONID": "A353E623783AC050406CEA0BBBDBCE85.pharmapp402pw2",
            "_ga": "GA1.2.1906271701.1568517673",
            "_abck": "C1333F16A61051CFD776EF8EE8D7A973~-1~YAAQxzLFF7JlTQ9tAQAAjF/wMgJVCL5ndD9F5ok8gCi6URGOvOZR4t1NpnO/H48o9Hg+ILWHjdDKVq6Irar9GxQEvPW2AboVDexef5slvU39u0ZGSbN6RGj727TZ+tCNHLqV9XLnZtHAUe4AZ9yBVqkCIiLd1H8ERnpaxMwy2r+PVpKTi/bV/2m1M6OGLMIZABvRQXD1ctxVCYi++1Hrabn7DCfbqIE/Gk8IWrdgwMjJ7FzBUH7fjpsM2vFCtlZGGiZtoSzqtXZZwqMDP1HiOtmrqjN5XJe1VS9m~-1~-1~-1",
            "check": "true",
            "segmentGroup": "60",
            "spcTarget": "true",
            "ra_id": "xxx1568517677443%7CG%7C0",
            "mbox": "session#88dc23bb7c44406fa10fb376fd350421#1568519538|PC#88dc23bb7c44406fa10fb376fd350421.28_53#1631762478",
            "aam_uuid": "016d32f061db0015d65d755e100503078002107000bd0",
            "KI_FLAG": "false",
            "X-Zip": "94587",
            "AMCVS_F6D93025512D2B0A0A490D44%40AdobeOrg": "1",
            "s_ecid": "MCMID%7C08854522879716665691184515543536746579",
            "AMCV_F6D93025512D2B0A0A490D44%40AdobeOrg": "-1303530583%7CMCIDTS%7C18155%7CMCMID%7C08854522879716665691184515543536746579%7CMCAAMLH-1569122477%7C9%7CMCAAMB-1569122477%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1568524877s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0",
            "utag_main": "v_id:016d32f061db0015d65d755e100503078002107000bd0$_sn:1$_ss:1$_st:1568519477532$ses_id:1568517677532%3Bexp-session$_pn:1%3Bexp-session$_tntCampaign:undefined%3Bexp-session$_metrics:undefined$segGroup:8",
            "_fbp": "fb.1.1568517679389.1250888833",
            "cto_lwid": "a802949e-8279-420c-855b-8d448cfe748c",
            "_derived_epik": "dj0yJnU9QXdETmZUeHZOSVVlbUIzbE04UFM3eXdHWi1hNXRPblImbj1LU2VlcG5QX19xMi0zb09lSmxMcjNRJm09NyZ0PUFBQUFBRjE5cmk4",
            "sn.isOfficeTime": "isOfficeTime||true",
            "__idcontext": "eyJjb29raWVJRCI6Ik5YR0pCT1MyT01XS1AzVjdMSVNTMkxNT0I0SkVXTzRLQVFJTUoyVUwySk5RPT09PSIsImRldmljZUlEIjoiTlhHSkJPUzJQWkxLTFROQktZNlNTRFZQQllZUUFFV1dKVVNQVjRWWFNWTkE9PT09IiwiaXYiOiJEM1pNNzZKM1o3SFVZNEhSN09PVVgzT1BERT09PT09PSIsInYiOjF9",
            "sn.vi": "84d81c8c-059a-4d0f-a68a-831eab2fe501",
            "__gads": "ID=c96c6d390331ec7e:T=1568517680:S=ALNI_MbGGqY5X74kpma5-FFBZUm2UtsRjw",
            "__CT_Data": "gpv=1&ckp=tld&dm=kmart.com&apv_154_www04=1&cpv_154_www04=1",
            "ctm": "{'pgv':4883938785046707|'vst':2254044588515274|'vstr':7604573933875504|'intr':1568517729791|'v':1}",
            "_gid": "GA1.2.1068334625.1570601845",
            "_gali": "zipcode",
            "s_pers": "%20s_vnum%3D1726197677903%2526vn%253D1%7C1726197677903%3B%20s_cvp_v7%3D%255B%255B%2527Natural%252520Search%2527%252C%25271570601845295%2527%255D%255D%7C1728454645295%3B%20eVar2%3Dseo%253AGoogle%253Aother%7C1573193847630%3B%20eVar6%3Dseo%253AGoogle%253Aother%7C1571033847632%3B%20eVar7%3DNatural%2520Search%7C1570688247634%3B%20eVar21%3DOther%7C1573193847635%3B%20eVar24%3Dseo%253AGoogle%253Aother%7C1573193847637%3B%20eVar25%3DLanding%2520%253E%2520Web%7C1570688247639%3B%20s_fid%3D671E6A8B453CDCF1-1AF0A5665D6F302C%7C1633760528116%3B%20s_nr%3D1570602128119-Repeat%7C1602138128119%3B%20gpv_pn%3DFindPharmacy%2520%253E%2520Web%7C1570603928122%3B%20o_c76%3Dwww.google.com%7C1573194128132%3B%20s_vs%3D1%7C1570603928135%3B",
            "s_sess": "%20s_e30%3DAnonymous%3B%20s_cc%3Dtrue%3B%20s_cpc%3D0%3B%20c_m%3DGooglewww.google.com%3B%20s_sq%3Dsearskmartpharmacy%253D%252526pid%25253DFindPharmacy%25252520%2525253E%25252520Web%252526pidt%25253D1%252526oid%25253DSubmit%252526oidt%25253D3%252526ot%25253DSUBMIT%2526searskmartcom%253D%252526c.%252526a.%252526activitymap.%252526page%25253DKmart%25252520Stores%252526link%25253DSearch%252526region%25253DseoLocalMain%252526pageIDType%25253D1%252526.activitymap%252526.a%252526.c%3B",
        }

        headers = {
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "clientId": "kmartrx",
            "Referer": "https://pharmacy.kmart.com/newrx-find-pharmacy",
            "Connection": "keep-alive",
        }

        for zip_search in sgzip.for_radius(50):
            params = (
                ("finderInput", zip_search),
                ("fluIndicator", ""),
                ("otherVaccines", ""),
            )
            response = requests.get(
                "https://pharmacy.kmart.com/RxServices/kmartrx/fetchPharmFinderGB",
                headers=headers,
                params=params,
                cookies=cookies,
            )
            data = json.loads(response.content)
            stores.extend(data)
            logger.info(f"{len(data)} stores scraped for zipcode {zip_search}")

        for store in stores:
            if store["unitNumber"] not in seen:
                logger.info(store)
                logger.info()
                logger.info()
                logger.info()
                # Store ID
                location_id = store["unitNumber"]

                # Name
                location_title = store["name"]

                # Street
                street_address = store["address"]

                # Country
                country = "US"

                # State
                state = store["state"]

                # city
                city = store["city"]

                # zip
                zipcode = store["zipcode"]

                # Lat
                lat = store["latitude"]

                # Long
                lon = store["longitude"]

                # Phone
                phone = store["storePhoneNumber"]

                # hour
                hour_raw = store["pharmacyHours"].replace('<li>', ' ').replace('</li>', ' ')
                hour = ' '.join(hour_raw.split())
                # Store data
                locations_ids.append(location_id)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                states.append(state)
                zip_codes.append(zipcode)
                hours.append(hour)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                cities.append(city)
                countries.append(country)
                page_urls.append('<MISSING>')

                seen.append(store["unitNumber"])

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
            page_url
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
            page_urls
        ):
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
                    page_url
                ]
            )


scrape = Scraper(URL)
scrape.scrape()
