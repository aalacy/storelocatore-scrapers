import requests
from bs4 import BeautifulSoup
import random
import csv


class MetaClass(type):

    """ Singleton Design Pattern  """

    _instance = {}

    def __call__(cls, *args, **kwargs):
        """ if instance already exist dont create one  """

        if cls not in cls._instance:
            cls._instance[cls] = super(
                MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class Random_Proxy(object):

    def __init__(self):
        self.__url = 'https://www.sslproxies.org/'
        self.__headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.wikipedia.org/',
            'Connection': 'keep-alive',
        }
        self.random_ip = []
        self.random_port = []

    def random_proxy(self):
        """
        This is Private Function Client Should not have accesss
        :return: Dictionary object of Random proxy and port number
        """

        r = requests.get(url=self.__url, headers=self.__headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Get the Random IP Address
        for x in soup.findAll('td')[::8]:
            self.random_ip.append(x.get_text())

        # Get Their Port
        for y in soup.findAll('td')[1::8]:
            self.random_port.append(y.get_text())

        # Zip together
        z = list(zip(self.random_ip, self.random_port))

        # This will Fetch Random IP Address and corresponding PORT Number
        number = random.randint(0, len(z) - 50)
        ip_random = z[number]

        # convert Tuple into String and formart IP and PORT Address
        ip_random_string = "{}:{}".format(ip_random[0], ip_random[1])

        # Create a Proxy
        proxy = {'https': ip_random_string}

        # return Proxy
        return proxy

    def Proxy_Request(self, request_type='get', url='', **kwargs):
        """
        :param request_type: GET, POST, PUT
        :param url: URL from which you want to do webscrapping
        :param kwargs: any other parameter you pass
        :return: Return Response
        """
        while True:
            try:
                proxy = self.__random_proxy()
               # print("Using Proxy {}".format(proxy))
                r = requests.request(
                    request_type, url, proxies=proxy, headers=self.__headers, timeout=8, **kwargs)
                return r
                break
            except:
                pass


class Requests(metaclass=MetaClass):

    @staticmethod
    def request(request_type='get', url='https://www.youtube.com', **kwargs):
        while True:
            try:
                proxy = Random_Proxy().random_proxy()
                # print("Using Proxy {}".format(proxy.get('https', None)))
                r = requests.request(request_type,
                                     url,
                                     proxies=proxy,
                                     headers={
                                         'Accept-Encoding': 'gzip, deflate, sdch',
                                         'Accept-Language': 'en-US,en;q=0.8',
                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                         'Referer': 'http://www.wikipedia.org/',
                                         'Connection': 'keep-alive',
                                     },
                                     timeout=8, **kwargs)
                return r
            except:
                pass


if __name__ == "__main__":
    def write_output(data):
        with open('data.csv', mode='w') as output_file:
            writer = csv.writer(output_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_ALL)

            # Header
            writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
            # Body
            for row in data:
                writer.writerow(row)

    def fetch_data():
        return_main_object = []
        addresses = []
        # search = sgzip.ClosestNSearch()
        # search.initialize()
        # MAX_RESULTS = 50
        # MAX_DISTANCE = 10
        # current_results_len = 0     # need to update with no of count.
        # zip_code = search.next_zip()
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        # }
        # while zip_code:
        #     result_coords = []
        #     print("remaining zipcodes: " + str(len(search.zipcodes)))

        # print("zip_code === "+zip_code)
        location_url = "https://publix.know-where.com/publix/cgi/selection?place=33802&keys=00793%2C01399%2C00425%2C01212%2C01103%2C00791%2C00671%2C01171%2C01410%2C00356%2C01707%2C00702%2C00352%2C01270%2C01651&async=results&apikey=js_main&stype=place"
        # location_url = "https://publix.know-where.com/publix/cgi/selection?place=" + \
        #     str(zip_code) + "&keys=00793%2C01399%2C00425%2C01212%2C01103%2C00791%2C00671%2C01171%2C01410%2C00356%2C01707%2C00702%2C00352%2C01270%2C01651&async=results&apikey=js_main&stype=place"
        # print(location_url)
        r = Requests.request(request_type='get', url=location_url).json()
        # print("location_url ==== ",r)
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        # it always need to set total len of record.

        current_results_len = len(r["locations"])
        base_url = "https://www.publix.com"

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
        if "locations" in r:
            for data in r["locations"]:
                # print(data)
                street_address = data["data"]['ADDR']
                # print(street_address)
                hours_of_operation = "Store hours " + \
                    data["data"]['STRHOURS'] + ' Pharmacy hours ' + \
                    data["data"]['PHMHOURS']
                hours_of_operation = hours_of_operation.replace(
                    "<br>", ",").strip()
                phone = data["data"]['PHONE']
                if "-" == phone:
                    phone = "<MISSING>"
                # print(phone)
                # print(hours_of_operation)
                # do your logic.
                # result_coords.append(
                #     (data["data"]['CLAT'], data["data"]['CLON']))
                store = [locator_domain, data["data"]['NAME'], data["data"]['ADDR'], data["data"]['CITY'], data["data"]['STATE'], data["data"]['ZIP'], country_code,
                         store_number, phone, location_type,  data["data"]['CLAT'],  data["data"]['CLON'], hours_of_operation.strip(), page_url]

                if store[2] + store[-3] in addresses:
                    continue
                addresses.append(store[2] + store[-3])
                store = [x.encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store
                # return_main_object.append(store)

            # if current_results_len < MAX_RESULTS:
            #     # print("max distance update")
            #     search.max_distance_update(MAX_DISTANCE)
            # elif current_results_len == MAX_RESULTS:
            #     # print("max count update")
            #     search.max_count_update(result_coords)
            # else:
            #     raise Exception("expected at most " +
            #                     str(MAX_RESULTS) + " results")
            # zip_code = search.next_zip()
            # break

    def scrape():
        data = fetch_data()
        write_output(data)

    scrape()
