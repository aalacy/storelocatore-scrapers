# -*- coding: utf-8 -*-
import csv
import urllib2
import requests
import sgzip
import usaddress

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'
           }
headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "raw_address","street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    alllocs = []
    for code in sgzip.for_radius(100):
        print('Pulling Zip Code %s...' % code)
        url = 'https://fit4mom.com/__/frontdesk/locations?zip=' + code + '&_=1565982065744'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<h2 class="contentTitle"><a href="' in line:
                lurl = line.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
        for loc in locs:
            LFound = True
            while LFound:
                LFound = False
                #try:
                r = session.get(loc + '/locations', headers=headers2)
                for line in r.iter_lines():
                    if '<div class="contentImg imgShape' in line:
                        locurl = loc + line.split('href="')[1].split('"')[0]
                        website = 'fit4mom.com'
                        country = 'US'
                        typ = 'Studio'
                        STFound = True
                        if locurl not in alllocs:
                            alllocs.append(locurl)
                            while STFound:
                                STFound = False
                                #try:
                                r2 = session.get(locurl, headers=headers2)
                                lines = r2.iter_lines()
                                hours = '<MISSING>'
                                lat = '<MISSING>'
                                lng = '<MISSING>'
                                store = '<MISSING>'
                                address = '<INACCESSIBLE>'
                                city = '<INACCESSIBLE>'
                                state = '<INACCESSIBLE>'
                                zc = '<INACCESSIBLE>'
                                phone = '<MISSING>'
                                name = '<MISSING>'
                                rawadd = '<MISSING>'
                                print('Pulling Location %s...' % locurl)
                                for line2 in lines:
                                    if '<h2 class="contentTitle" itemprop="name">' in line2:
                                        name = line2.decode('utf-8','ignore').encode("utf-8").split('<h2 class="contentTitle" itemprop="name">')[1].split('<')[0].replace('"',"'")
                                    if '<p class="address" itemprop="address">' in line2:
                                        g = next(lines)
                                        g = g.replace('•','').replace(' ','').replace('<br>United States','').replace('\r','').replace('\n','').replace('\t','').strip()
                                        g = g.replace('<br>',', ')
                                        rawadd = g.replace('"',"'")
                                        try:
                                            add = usaddress.tag(g)
                                            baseadd = add[0]
                                            if 'AddressNumber' not in baseadd:
                                                baseadd['AddressNumber'] = ''
                                            if 'StreetName' not in baseadd:
                                                baseadd['StreetName'] = ''
                                            if 'StreetNamePostType' not in baseadd:
                                                baseadd['StreetNamePostType'] = ''
                                            if 'PlaceName' not in baseadd:
                                                baseadd['PlaceName'] = '<INACCESSIBLE>'
                                            if 'StateName' not in baseadd:
                                                baseadd['StateName'] = '<INACCESSIBLE>'
                                            if 'ZipCode' not in baseadd:
                                                baseadd['ZipCode'] = '<INACCESSIBLE>'
                                            address = add[0]['AddressNumber'] + ' ' + add[0]['StreetName'] + ' ' + add[0]['StreetNamePostType']
                                            address = address.encode('utf-8')
                                            if address == '':
                                                address = '<INACCESSIBLE>'
                                            city = add[0]['PlaceName'].encode('utf-8')
                                            state = add[0]['StateName'].encode('utf-8')
                                            zc = add[0]['ZipCode'].encode('utf-8')
                                        except:
                                            rawadd = g
                                    if '<h2 class="contentTitle">Contact' in line2:
                                        try:
                                            phone = next(lines).split('<li>')[1].split(' ')[0].encode('utf-8')
                                        except:
                                            phone = '<MISSING>'
                                    phone = phone.replace('<em>','').replace('</em>','')
                                yield [website, name, rawadd, address, city, state, zc, country, store, phone, typ, lat, lng, hours]
##                            except:
##                                STFound = True
##                except:
##                    LFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
