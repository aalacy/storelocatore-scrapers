from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://modoyoga.com/"


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
        stores = []
        countries = []
        location_types = []
        page_urls = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        driver.get('https://modoyoga.com/search-results/?userLocation=')
        stores = [card for card in driver.find_elements_by_css_selector('div.row.full-studio-card')]

        for store in stores:
            if store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].split(',')[-1].strip() in ['USA', 'Canada']:
                # Name
                location_title = store.find_element_by_css_selector('div.title').get_attribute('textContent').strip()

                # Page url
                page_url = [url.get_attribute('href') for url in store.find_elements_by_css_selector('a') if url.get_attribute('href')][0]

                # Store ID
                location_id = store.get_attribute('data-studio-id').split('-')[1]

                # Type
                location_type = 'Yoga'

                # Street
                street_address = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].strip().split(',')[0]

                # zip
                zipcode = '<MISSING>'

                # Phone
                phone = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[1].strip()

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Country
                country = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].split(',')[-1]

                # Store data
                locations_ids.append(location_id)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                zip_codes.append(zipcode)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                countries.append(country)
                location_types.append(location_type)
                page_urls.append(page_url)

        for page_url in page_urls:
            driver.get(page_url)
            print(f'Getting information for {page_url}')

            try:
                # city
                city = driver.find_element_by_css_selector('div.col-6.offset-1 > p').get_attribute('textContent').split('<br>')[-1].split(',')[0]

                # State
                state = driver.find_element_by_css_selector('div.col-6.offset-1 > p').get_attribute('textContent').split('<br>')[-1].split(',')[1]
            except:
                city = '<MISSING>'
                state = '<MISSING>'

            try:
                # Hour
                hour = [hour.get_attribute('textContent') for hour in driver.find_elements_by_css_selector('div.row > p') if 'pm' in hour.get_attribute('textContent')][0]
            except:
                hour = '<MISSING>'

            states.append(state)
            hours.append(hour)
            cities.append(city)


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
                    self.url.strip(),
                    page_url.strip(),
                    locations_title.strip(),
                    street_address.strip(),
                    city.strip(),
                    state.strip(),
                    zipcode.strip(),
                    country.strip(),
                    location_id.strip(),
                    phone_number.strip(),
                    location_type.strip(),
                    latitude.strip(),
                    longitude.strip(),
                    hour.strip(),
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
