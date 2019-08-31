const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape(){
  return await axios({
    method: 'GET',
    url: 'https://choiceoneuc.com/locations/'
  }).then(async (resp) => {
     dom = new JSDOM(resp.data);
     document = dom.window.document;
     rows = document.querySelectorAll('div.store')
     data = [];
     for (let row of rows){
        latlon = await retrieveLatLon(row.querySelector('a').getAttribute('href'));
        row = sanitize(row.textContent);
        area = parseArea(row[2]);
        phone = row[3].replace('Phone:', '').trim();
        hours = row[5].replace('Hours:', '').trim();
       
        data.push({
          locator_domain: 'choiceoneuc.com',
          location_name: row[0],
          street_address: row[1],
          city: area.city,
          state: area.state,
          zip: area.zip,
          country_code: 'US',
          store_number: '<MISSING>',
          phone: phone,
          location_type: '<MISSING>',
          latitude: latlon.lat,
          longitude: latlon.lon,
          hours_of_operation: hours,
        })
     }
     return data;
  })
}

async function retrieveLatLon(targetUrl){

    return await axios({
      method: 'GET',
      url: targetUrl
    }).then((resp) => {
      map = new JSDOM(resp.data).window.document;

      //If the google maps iframe isn't in the page, then bail outskis
      link = map.querySelector('iframe')
    
      //If we've got a null iframe, there's no map available
      if (link == null){return {lat: '<MISSING>', lon: '<MISSING>'}}
      
      //If we're not null, extract the src attribute
      link = link.getAttribute('src');

      //If google maps is passed a midpoint, we don't have a valid latlon string to parse
      if (link.includes('mid=')){return {lat: '<MISSING>', lon: '<MISSING>'} }
      
      link = link.replace(/^.*2d-/, '') //strip leading
      link = link.split('!') // split out params
      return {
        lat: "-" + link[0],
        lon: link[1].replace(/[0-9]d/, '')
      }
    })

}

function latLonFromUrl(url){
  url = url.replace(/^.*2d-/, '');
  console.log(url)
}

function sanitize(textRow){
  sane = [];
  for (s of textRow.split("\n")){
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
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