const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');
const striptags = require('striptags')

Apify.main(async () => {
  usData = await scrape('https://www.chronictacos.com/locations', 'US'); //US Locations
  // caData = await scrape('https://www.chronictacos.com/canada-locations', 'CA') //CA Locations
});

async function scrape(url, countryCode) {
  return await axios({
    method: 'GET',
    url: 'https://www.chronictacos.com/locations'
  }).then(async (resp) => {
      document = new JSDOM(resp.data).window.document;
      rows = document.querySelectorAll('.span4');
      for (let row of rows){        
        if (row.querySelector('.fp-el') == null){continue;}
        try {
          addr = dataMassage(row.querySelector('.fp-el').innerHTML.split('<br>'));
          area = parseArea(striptags(addr[1]));
        } catch (e) {
          console.log(e);
        }
        

        // await Apify.pushData([{
        // console.log([{
        //   locator_domain: 'chronictacos.com',
        //   location_name: store,
        //   street_address: address,
        //   city: area[0].trim(),
        //   state: area[1].trim(),
        //   zip: area[2].trim(),
        //   country_code: countryCode,
        //   store_number: '<MISSING>',
        //   phone: phone,
        //   location_type: '<MISSING>',
        //   latitude: latlon.lat,
        //   longitude: latlon.lon,
        //   hours_of_operation: hours,
        // }]);

      }
  })
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

function dataMassage(d){
  if (d[0].startsWith('420')){
    b = strd[0].split('Birmingham')
    return [striptags(b[0]), 'Birmingham ' + striptags(b[1]), striptags(d[1])];
  }

  if (d.length == 4){return [d[0] + " " + d[1], d[2], d[3]];}

  return d;
}
