const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  return await axios({
    method: 'GET',
    url: 'https://www.chromehearts.com/locations'
  }).then((resp) => {
    data = [];
    document = new JSDOM(resp.data).window.document;
    rows = document.querySelectorAll('.v-locations__data-simple > li')
    
    for (let row of rows){
      location = row.querySelector('strong').textContent
      latlon = latLonFromLink(row.querySelector('a.address-link').getAttribute('href'));
      address = row.querySelector('a.address-link').innerHTML.split('<br>');
      if (address.length == 3){
        address = [address[0] + " " + address[1], address[2]] 
      }
      phone = row.querySelector('a.phone').textContent.replace('Tel:').trim();
      area = parseArea(address[1]);
      data.push({
        locator_domain: 'chromehearts.com',
        location_name: location,
        street_address: address[0],
        city: area.city,
        state: area.state,
        zip: area.zip,
        country_code: 'US',
        store_number: '<MISSING>',
        phone: phone,
        location_type: '<MISSING>',
        latitude: latlon.lat,
        longitude: latlon.lon,
        hours_of_operation: '<MISSING>',
      })
    }
    return data;
  })

}

function latLonFromLink(href){
  [lat, lon] = href
    .replace(/^.*\@/, '') //strip everything up to latlong string
    .replace(/\/.*/, '') // strip everything after latlong string
    .split(','); //split on comma
  return {lat: lat, lon: lon}
}

function parseArea(area){
  parsed = {city: '', state: '', zip: ''};
  area = area.split(',');
  parsed.city = area[0];
  area = area[1].split(' ');
  parsed.zip = area.pop();
  parsed.state = area.join(' ').trim();
  return parsed;
}