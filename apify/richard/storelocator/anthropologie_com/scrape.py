import requests

from Scraper import Scrape

URL = "https://www.anthropologie.com/"


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
        location_types = []
        page_urls = []

        cookies = {
            'bm_sz': '4220936B45BD4A5EF2BD0FEF6870B6C0~YAAQpccGF5AhMHduAQAA4rnpxAVq6T3RvIwVKk0KP57RWr8NKWXbghFoYUwDtYiEF0mNSuipR59WEjsyDrZB6RbRXyoo2vKAARJKtp7nLQFXVypu8UOFpqxdRCMMG1ze3QNCr973tnHzBAG6gW3nh4NkcrkaOKtzEk4YCn4Yxi9YXi0pTfmeqtY6Q55EQ0w20B4LLSGKhg==',
            'SSLB': '1',
            'SSID': 'CABauB0cAAAAAADyleRdkPVABvKV5F0BAAAAAACeysVf8pXkXQBzWk-7AAOd3RgA8pXkXQEAUbsAA6PdGADyleRdAQA',
            'SSSC': '439.G6765697406936872336.1|47951.1629597:47953.1629603',
            'urbn_geo_region': 'US-NV',
            'urbn_language': 'en-US',
            'urbn_country': 'US',
            'urbn_auth_payload': '%7B%22authToken%22%3A%20%22eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhbiIsImV4cCI6MTU3NTI2MjI4Mi4zOTEyMDA1LCJpYXQiOjE1NzUyNjE2ODIuMzkxMjAwNSwiZGF0YSI6IntcImNyZWF0ZWRUaW1lXCI6IDE1NzUyNjE2ODIuMzkwMjUzNSwgXCJwcm9maWxlSWRcIjogXCJLWFA4OU9ZdUhGY0hpSVhYYjV0UHZXZEw4RVBKYk9Sc1ZoYnBGTWpJMGdnUk1PS0kxYUhVNW01ZXN5VFllVEF4NVUrM3JzMnJ4aGptNHBEMzBDY0lCdz09NmY2NjhiZmVlMDY2ZWI1MTYxMTRhOTRiMmE1ZDY3MmM0NzJmMjdjZWMzM2QyMWNhMGFkNmE2MThlYmVlY2E1YlwiLCBcImFub255bW91c1wiOiB0cnVlLCBcInRyYWNlclwiOiBcIkYxV1Q1OE4yR1JcIiwgXCJjYXJ0SWRcIjogXCI4RlUvYytRckNWbzl0MkpicGRVY2Yrd1VibjVsMnpMNTcxZHZNRVJvU1VRV3Y4cUxreit4Q09lRllOYjRQNGhSNVUrM3JzMnJ4aGptNHBEMzBDY0lCdz09ZDUyMDFlMzhjMjIyZmQ5YWFmYmVlMjViNjlhNDczMGVjMTI4MWE4NDVhMjc5NDc5ZjY3MWJlNmJlZjQ2MGE0NVwiLCBcInNjb3BlXCI6IFtcIkdVRVNUXCJdLCBcInNpdGVJZFwiOiBcImFuLXVzXCIsIFwiYnJhbmRJZFwiOiBcImFuXCIsIFwic2l0ZUdyb3VwXCI6IFwiYW4tdXNcIiwgXCJkYXRhQ2VudGVySWRcIjogXCJVUy1OVlwiLCBcImdlb1JlZ2lvblwiOiBcIlVTLU5WXCIsIFwiZWRnZXNjYXBlXCI6IHtcInJlZ2lvbkNvZGVcIjogXCJDQVwifX0ifQ.FafREkeYSN6EF6OcvB9Z2w4fwzBfJi1Jm-x7605hnXo%22%2C%20%22reauthToken%22%3A%20%22eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhbiIsImV4cCI6MTU5MDgxMzY4Mi4zOTE2OSwiaWF0IjoxNTc1MjYxNjgyLjM5MTY5LCJkYXRhIjoie1wiY3JlYXRlZFRpbWVcIjogMTU3NTI2MTY4Mi4zOTE2NzUsIFwic2NvcGVcIjogW1wiR1VFU1RcIl0sIFwidHJhY2VyXCI6IFwiRjFXVDU4TjJHUlwiLCBcInByb2ZpbGVJZFwiOiBcIktYUDg5T1l1SEZjSGlJWFhiNXRQdldkTDhFUEpiT1JzVmhicEZNakkwZ2dSTU9LSTFhSFU1bTVlc3lUWWVUQXg1VSszcnMycnhoam00cEQzMENjSUJ3PT02ZjY2OGJmZWUwNjZlYjUxNjExNGE5NGIyYTVkNjcyYzQ3MmYyN2NlYzMzZDIxY2EwYWQ2YTYxOGViZWVjYTViXCJ9In0.7E0Xa-Kg8gAajnyvZKmKSscc2h7H84-nFGE8tJ4kkRM%22%2C%20%22expiresIn%22%3A%20600.0%2C%20%22reauthExpiresIn%22%3A%2015552000.0%2C%20%22scope%22%3A%20%22GUEST%22%2C%20%22tracer%22%3A%20%22F1WT58N2GR%22%2C%20%22dataCenterId%22%3A%20%22US-NV%22%2C%20%22geoRegion%22%3A%20%22US-NV%22%2C%20%22createdAt%22%3A%201575261682395.5867%2C%20%22authExpiresTime%22%3A%201575262162.3955889%2C%20%22reauthExpiresTime%22%3A%201590813682.39559%7D',
            'AKA_A2': 'A',
            'urbn_tracer': 'F1WT58N2GR',
            'urbn_data_center_id': 'US-NV',
            'urbn_site_id': 'an-us',
            'urbn_channel': 'web',
            'urbn_edgescape_site_id': 'an-us',
            'urbn_inventory_pool': 'US_DIRECT',
            'urbn_currency': 'USD',
            'urbn_personalization_context': '%5B%5B%22device_type%22%2C%20%22LARGE%22%5D%2C%20%5B%22personalization%22%2C%20%5B%5B%22ab%22%2C%20%5B%5D%5D%2C%20%5B%22experience%22%2C%20%5B%5B%22image_quality%22%2C%2080%5D%2C%20%5B%22reduced%22%2C%20false%5D%5D%5D%2C%20%5B%22initialized%22%2C%20true%5D%2C%20%5B%22isCallCenterSession%22%2C%20false%5D%2C%20%5B%22isSiteOutsideNorthAmerica%22%2C%20false%5D%2C%20%5B%22isSiteOutsideUSA%22%2C%20false%5D%2C%20%5B%22isViewingInEnglish%22%2C%20true%5D%2C%20%5B%22isViewingRegionalSite%22%2C%20true%5D%2C%20%5B%22loyalty%22%2C%20false%5D%2C%20%5B%22loyaltyPoints%22%2C%20%22%22%5D%2C%20%5B%22siteDown%22%2C%20false%5D%2C%20%5B%22thirdParty%22%2C%20%5B%5B%22dynamicYield%22%2C%20true%5D%2C%20%5B%22googleMaps%22%2C%20true%5D%2C%20%5B%22moduleImages%22%2C%20true%5D%2C%20%5B%22personalizationQs%22%2C%20%22%22%5D%2C%20%5B%22productImages%22%2C%20true%5D%2C%20%5B%22promoBanners%22%2C%20true%5D%2C%20%5B%22tealium%22%2C%20true%5D%5D%5D%2C%20%5B%22userHasAgreedToCookies%22%2C%20false%5D%5D%5D%2C%20%5B%22scope%22%2C%20%22GUEST%22%5D%2C%20%5B%22user_location%22%2C%20%2287b729812e351a4441559c6f7d1572f4%22%5D%5D',
            'localredirected': 'False',
            'siteId': 'an-us',
            'ak_bmsc': '4FD2718C5850CCDD6584CFD0FDF7CFA7173DC3AB37290000F495E45D843A730F~pl1fU6QC2K9S1TxxbmDmIujjMWTysXrp8S2bFVBCqPGWDH4odRHJjGsECfqySqbmGDnhxdJnslVCZeYZ7JKNFcj46oJmLxY/p28qJsoCm9e8UpnNYH2TW7i1jl3+37W6AYpQq/sBXb8JIcnpAETH/NOGULR+4bLo7uhd7lyzcNOSWI4Ig6r0QS/bPl+Z63j/DDLyjMRFERmTe0WeV2HEVN/9iLjYsYO9D5BdJLo8uugAg=',
            'akacd_ss1': '3752714481~rv=51~id=da7997edc2638668f383585b0e9a52e9',
            '_dy_csc_ses': 't',
            '_dy_c_exps': '',
            '_dycnst': 'dg',
            '_dyid': '8174033630195389940',
            '_dyjsession': 'cd026cbab0c2d421b7e5f0f23900425c',
            '_dy_geo': 'US.NA.US_CA.US_CA_Union%20City',
            '_dy_df_geo': 'United%20States.California.Union%20City',
            '_dy_toffset': '-1',
            'SSRT': '9ZXkXQADAA',
            'spacookie': '1',
            'new_visitor': 'visitor',
            'persist_user': 'true',
            '_abck': '086621030059E1C91CFDAC2A46A4647C~0~YAAQq8M9F4ZMtnRuAQAAm8rpxAILvd3CuRZiTzHY2gfSNOCYS+c1AMxkqftUEBcaL1JdvbCusIdk0D/eRRkU49s3Y8ubxcJ28jAXdd6lz06I3j3y/Mdk+APLuVuSmyAWiGlloXjENtEifEoYzAUe7QM29r1Nvnmpm33w0Hrf6ILqj+jnbxWrXuJyjUAMuOaH4ZWnWmOuoJfUy2hSTaYX+yRxLZKkR5t+bIb/ABv3ZF+e0uqK6enoIZIsIErXTJrpHZ1LFpUUe+NKciC3i6ANICmQP58eHFNVgB9gCWjroUSEKY/m0E4igSV989WavG8OvCFLbR1mM/ZFGEuytOg=~-1~-1~-1',
            '_ga': 'GA1.2.243342171.1575261687',
            '_gid': 'GA1.2.278391770.1575261687',
            'gbi_sessionId': 'ck3ny4whg00003g989j0drt1g',
            'gbi_visitorId': 'ck3ny4whh00013g98n2h0tfjh',
            '_gcl_au': '1.1.1517376915.1575261687',
            'ab.storage.deviceId.6f0baa4c-4dbf-4b0d-9945-ddc58ab07a55': '%7B%22g%22%3A%22ceff38af-ff78-3a37-b9d3-a310eea60b50%22%2C%22c%22%3A1575261686810%2C%22l%22%3A1575261686810%7D',
            '_pxff_tm': '1',
            '_gat_tealium_0': '1',
            '_fbp': 'fb.1.1575261687046.610193464',
            '__attentive_id': 'dc256684bc164e79a3c564fabcd45c50',
            '_dy_ses_load_seq': '31398%3A1575261696745',
            '_dy_c_att_exps': '',
            '_dyfs': '1575261697097',
            '_dycst': 'dk.m.c.ss.',
            'urbn_page_visits_count': '%7B%22an-us%22%3A2%7D',
            'urbn_device_type': 'MEDIUM',
            'bm_sv': '9F5C745FE69B5A3935377B37ABCB8C1E~O1pFxeTyjX0fyrytG4lth/lZ5+9XT4ExBLPZKgRazpRBDdWHeJa8mwzMyaCCejL9Eo/sl3GQxxD9viEzojNu5yCSIL/NFFZAPRBN9xOL4igLuCNAqeXXYnrdkMEMQhQDhIQruIiQVAIiBbL1ky5XFgDKDg9R82RcN9YDskvswPw=',
            'mp_anthropologie_mixpanel': '%7B%22distinct_id%22%3A%20%2216ec4e9cc5684d-0da874eabcae8-1d3a6a5b-1fa400-16ec4e9cc57ae5%22%2C%22bc_persist_updated%22%3A%201575261686877%2C%22customer_language%22%3A%20%22english%22%7D',
            'ab.storage.sessionId.6f0baa4c-4dbf-4b0d-9945-ddc58ab07a55': '%7B%22g%22%3A%22390d2d12-7fcb-9467-b371-23eb2a0cdbcd%22%2C%22e%22%3A1575263500757%2C%22c%22%3A1575261686808%2C%22l%22%3A1575261700757%7D',
            'stc115251': 'tsa:1575261687840.71498045.33394146.8630825245733056.1:20191202051140|env:1%7C20200102044127%7C20191202051140%7C2%7C1048047:20201201044140|uid:1575261687839.485538915.6556711.115251.1196293751.:20201201044140|srchist:1048047%3A1%3A20200102044127:20201201044140',
            '__attentive_pv': '2',
            '_px3': '0c5f4483af51156bb5f43649586180c1c1ef190da49c640073c7e0c8c0256e14:V0RZgtLX0ZFO58oNLmEK9d77cX+9qOJQJzPjGZ4UT52g5dQMt3krPqIZdZk3qqLU6QBnc7y6y3NcFAUHvWVaRw==:1000:PTT/1EgNAhQgrbGMHnPVtqKqJzPbSWY3KYYzZoeWgOwaep3zFkjM79UmjNq3PKcQSOg3I5yWPJ/EXuvgX4JDI33YJnC4jiQo4SfNLRPhu5FFanNj9g+0IrUC9CjVJ/7JZCPiLMkJQdNlGmFTJYRZ0bjyLXoK7l5GOvZ1/UNaap8=',
            '_derived_epik': 'dj0yJnU9VDhlNnpFZ1hSVmpYR2JCQzBlNkZ4MGtwSlNyS0t6Rm0mbj0yT3B5MndZNlpPdmx0Y1k2TWN0aF9nJm09NyZ0PUFBQUFBRjNrbGdV',
            'akavpau_a15_anthropologie_vp_us': '1575262003~id=1b7ae72ab035417ba7e1a35de8681bec',
            '_dy_soct': '217641.320721.1575261684*252999.381793.1575261685*165296.236604.1575261696*264076.403652.1575261696*266362.407936.1575261697*371188.792707.1575261703',
            'cybermondayea-sess': 'true',
            'cybermondayea-perm': 'true',
            'utag_main': 'v_id:016ec4e9c54d0020737544e9df6003078003207000bd0$_sn:1$_ss:0$_st:1575263504019$ses_id:1575261685071%3Bexp-session$_pn:2%3Bexp-session$isLoggedIn:false%3Bexp-session',
            'RT': 'sl=2&ss=1575261682083&tt=13951&obo=0&bcn=%2F%2F17c8edc9.akstat.io%2F&sh=1575261701278%3D2%3A0%3A13951%2C1575261688210%3D1%3A0%3A6117&dm=anthropologie.com&si=add436ec-6c98-495e-9e68-6ac71fa3a52a&ld=1575261701279&nu=https%3A%2F%2Fwww.anthropologie.com%2Fstores&cl=1575261723836',
        }

        headers = {
            'authority': 'www.anthropologie.com',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.anthropologie.com/stores',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        params = (
            ('brandId', '54|04'),
            ('distance', '100'),
            ('urbn_key', '937e0cfc7d4749d6bb1ad0ac64fce4d5'),
        )

        stores = [store for store in requests.get('https://www.anthropologie.com/api/misl/v1/stores/search', headers=headers, params=params, cookies=cookies).json()['results'] if 'storeInventory' in store.keys()]

        for store in stores:
            if ('closed' not in store.keys() or not store['closed']) and (store['addresses']['marketing']['country'] in ['US', 'Canada']):
                # Store ID
                location_id = store['id']

                # Name
                location_title = store['addresses']['marketing']['name']

                # Page url
                page_url = '<MISSING>'

                # Type
                location_type = 'Retail'

                # Street
                street_address = store['addresses']['marketing']['addressLineOne']

                # city
                city = store['addresses']['marketing']['city']

                # zip
                zipcode = store['addresses']['marketing']['zip']

                # State
                state = store['addresses']['marketing']['state']

                # Phone
                phone = store['addresses']['marketing']['phoneNumber']

                # Lat
                lat = store['loc'][0]

                # Long
                lon = store['loc'][1]

                # Hour
                hour = ' '.join([
                    f"Sunday: {store['hours']['1']['open']} - {store['hours']['1']['close']}",
                    f"Monday: {store['hours']['2']['open']} - {store['hours']['2']['close']}",
                    f"Tuesday: {store['hours']['3']['open']} - {store['hours']['3']['close']}",
                    f"Wednesday: {store['hours']['4']['open']} - {store['hours']['4']['close']}",
                    f"Thursday: {store['hours']['5']['open']} - {store['hours']['5']['close']}",
                    f"Friday: {store['hours']['6']['open']} - {store['hours']['6']['close']}",
                    f"Saturday: {store['hours']['7']['open']} - {store['hours']['7']['close']}",
                ])

                # Country
                country = store['addresses']['marketing']['country']

                # Store data
                locations_ids.append(location_id)
                page_urls.append(page_url)
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

        for (
                locations_title,
                page_url,
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
            page_urls,
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
            self.data.append(
                [
                    self.url,
                    page_url,
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
