
import base
import requests, json
from urllib.parse import urljoin

class Scrape(base.Spider):

    def crawl(self):
        base_url = "http://genesishcc.com/"
        json_body = requests.post("http://genesishcc.com/DesktopModules/R2i.Genesis.CenterSearch/SearchResults.aspx/Search",
                                  data="""{ centerLat: "49.2587",centerLong: "24.62779999999998",term: "geoloc:49.2587,24.62779999999998",clientGeocodedLat: "0",clientGeocodedLng: "0",clientReverseGeocodeCity: "",clientReverseGeocodeCounty: "",clientReverseGeocodeState: "",type: "location",distance: "50000",nearby: "false",limit: "999",services: [],amenities: [],careoptions: [] }""",
                                  headers={
                                      "Accept": "application/json, text/javascript, */*; q=0.01",
                                      "Origin": "http://genesishcc.com",
                                      "X-Requested-With": "XMLHttpRequest",
                                      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                                      "Content-Type": "application/json; charset=UTF-8",
                                      "Referer": "http://genesishcc.com/our-services/find-a-location",
                                      "Accept-Encoding": "gzip, deflate"
                                  }).json()
        for result in json_body.get('d', {}).get('Results',[]):
            href = result.get('URLCode')
            if href:
                i = base.Item(result)
                i.add_value('locator_domain', urljoin(base_url, href))
                i.add_value('location_name', result.get('Name','').strip())
                i.add_value('street_address', result.get('Address','').strip())
                i.add_value('city', result.get('City','').strip())
                i.add_value('state', result.get('State','').strip())
                i.add_value('zip', result.get('Zip','').strip())
                i.add_value('phone', result.get('Phone','').strip())
                i.add_value('country_code', base.get_country_by_code(i.as_dict().get('state')))
                i.add_value('latitude', result.get('Latitude',''))
                i.add_value('longitude', result.get('Longitude',''))
                yield i

if __name__ == '__main__':
    s = Scrape()
    s.run()
