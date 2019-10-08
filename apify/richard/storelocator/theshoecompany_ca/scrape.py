import json
import requests

from pypostalcode import PostalCodeDatabase
from Scraper import Scrape

URL = "https://www.theshoecompany.ca"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []

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
        location_types = []
        stores = []

        pcdb = PostalCodeDatabase()
        pc = 'T3Z'
        radius = 3000
        results = pcdb.get_postalcodes_around_radius(pc, radius)
        postalcodes = [p.postalcode for p in results]

        for postalcode in postalcodes:
            url = f'https://www.theshoecompany.ca/api/v1/stores/search?address={postalcode}&distance=100&locale=en_CA&pushSite=TSL_SC&sites=TSL_SC'

            r = requests.get(
                url=url,
                headers={
                    'cookie': 'bm_sz=3BB0478984C66DBCE6D52E5B9EE4ED74~YAAQJjPFFxF43mNtAQAAF7hLewVslpD0jhJmHDB4ihgg51cmdm2EmPuXiIHZX7IAhjFU5p5B4jWkLhKfAgfxGUPrL+io53l7I7WmSdDLdwUoSFcpzncVHe4QeG8HukYgW8+030zOL5ZjI3jxEvZAl2Io9NdY66K8pIwibCleC59zI833KMYzw/EArK5yjpxYD2YJDJ6bOw==; _abck=5138B76242C076D43B0E17E7386E18F6~-1~YAAQJjPFFxJ43mNtAQAAF7hLewKmnC16vvtSHGOOLvrTkX8cCubc7dXzoGActX45X45QD/sR4udIS1NAs0dKJnXtyL1bDQUzvi3rGtz613uUDnRRGPGLXzj9FyINzjvY+xYi4Y9e2HGpd8WYB2aRDKkP8UTEmTB/NDNik5lLjg5oiHToC2L4Ofl+cKnnJ3DCxdp2PKIVRQoxDeb65iH2JFZvs0BKEYKN0bnUDjBExL2UfcKintYs5vZOqcAeperAgGGX+T+smxdpW8pxCO/BhHLOs5pJU3DpETvr7A==~-1~-1~-1; _evga_3157=f86941228417a184.; JSESSIONID=U+7jKbzrYKrIK+wXrLp5OuNg.ATGPS08; TIER=GUEST; MOUS=3; _dynSessConf=5654863123688744674; BVBRANDID=a11874ba-26e4-4cfb-9ac7-8c841285fb35; BVBRANDSID=394a8f6c-e17e-4e29-a4bf-b81ed897f2ed; ak_bmsc=EFDF6D8C644167FB1687EF8B826C6E2E17C533264C2B00002634905DD03BBF51~pl8xGaniYcTpLiCCCrP/mmxw3m7YDhmIMS1o9Jcg7qDvYiJQEb858pHyPJWsalqanQGyhIf0BCzNucRqEtdorA4Zk1y6YT+X3AOZyTJpfcmGdMcsuOnRZ0QjmLrBQaqYvx1AuNPtvlpFr5jbw1h/wHHG6K3NsGacPbHeyktPPAfYOqk+kzE2BFRi3sCe33bjjWzS88dZmV78RgeP7N9v3WJlMOdopTd196caYfl/wivQbfczkMldPjFpmBaLEzofORlz9J4LWmFadCPZ+Q4l6+C0AYX7CKA9rJRiUwZnjyhGk=; cto_lwid=e34e3a00-5596-4f6f-b4bd-287466b4220d; _ga=GA1.2.1668866735.1569731626; _gid=GA1.2.1368967726.1569731626; AMCVS_6020C2D754D583630A4C98C6%40AdobeOrg=1; AMCV_6020C2D754D583630A4C98C6%40AdobeOrg=281789898%7CMCIDTS%7C18169%7CMCMID%7C08680147445304652151167050752523131749%7CMCAAMLH-1570336426%7C9%7CMCAAMB-1570336426%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1569738826s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.1.0; s_cc=true; _fbp=fb.1.1569731626165.845940868; s_fid=14386CAE18CC6428-2BD68C5034DC8FF8; s_vnum=1569913200686%26vn%3D1; s_invisit=true; aa_lv_s=First%20Visit; bm_sv=D0D36F4ECD99EA986BD3A619E625A970~HFneFsH+Q6C7kFleLAsnx8qMwhbIeg94nxdbR22uyH9/nUYjPh6rGbnlw/lPINKNJkIsfSNJ/WZLp5bnnI31vCVjeAO7X15lYkyfnumpDplRVQBJ+VNO2WCCycl1WWTeal+NT2g/oQo5+v06smkAkbpfXPk401Ehnt+kg1dFV10=; utag_main=v_id:016d7b4bc2d8001b5b728918aa9103078002407000bd0$_sn:1$_ss:0$_st:1569733455404$ses_id:1569731625689%3Bexp-session$_pn:1%3Bexp-session$_prevpage:tsc%3Bexp-1569735255405$vapi_domain:theshoecompany.ca; aa_lv=1569731655409; s_getNewRepeat=1569731655410-New; s_sq=%5B%5BB%5D%5D'
                }
            )
            try:
                stores.extend(json.loads(r.content)['Response']['sortedlist'].values())
            except:
                pass


        for store in stores:
            if store["locationId"] not in self.seen:
                # Store ID
                location_id = store["locationId"]

                # Name
                location_title = store['sites'][0]["description"]

                # Type
                location_type = '<MISSING>'

                # Street
                street_address = store["address1"] + store["address2"] if store["address2"] else store["address1"]

                # State
                state = store["state"]

                # city
                city = store["city"]

                # zip
                zipcode = store["postalCode"]

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store["phoneNumber"]

                # Hour
                hour = store["storeHours"]

                # Country
                country = store['country']

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
                location_types.append(location_type)
                self.seen.append(location_id)

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
                location_type,
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
            location_types,
        ):
            if country == "<MISSING>":
                pass
            else:
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
                        location_type,
                        latitude,
                        longitude,
                        hour,
                    ]
                )


scrape = Scraper(URL)
scrape.scrape()
