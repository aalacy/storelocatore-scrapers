const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'http://politospizza.com/locations.aspx';
 

async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
 
        const $  =cheerio.load(html);
        var items=[];

        var main = $('.about-locations').find('.col-md-6').find('div');

       
        function mainhead(i)

                    {
                        if(8>i)

                            {
         
            
            var location_name = main.eq(i).find('h1').text();
            var address_tmp = main.eq(i).find('h2').text();
            var hour = main.eq(i).find('h6').text().trimLeft().replace(/\n|\r/g, "").replace(/\s/g,'');
            var address_tmp1 = address_tmp.split('\n');
            var address = address_tmp1[1].trim();
            var phone = address_tmp1[3].trim();
            var city_tmp = address_tmp1[2].trim().split(',');
           
              if(city_tmp.length == 2){
                  var city = city_tmp[0];
                  var state_tmp = city_tmp[1].trim();
                  var state_tmp1 = state_tmp.split(' ');
                  var state = state_tmp1[0];
                  var zip = state_tmp1[1];
                

                }

                else if (city_tmp.length == 3){
                  var city = city_tmp[0];
                  var state = city_tmp[1];
                  var zip = city_tmp[2];
                  
                }


                        items.push({  

                          locator_domain: 'http://politospizza.com/', 

                          location_name: location_name, 

                          street_address: address,

                          city: city, 

                          state: state,

                          zip:  zip,

                          country_code: 'US',

                          store_number: '<MISSING>',

                          phone: phone,

                          location_type: 'politospizza',

                          latitude: '<MISSING>',

                          longitude: '<MISSING>', 

                          hours_of_operation: hour
                        }); 

            
                       mainhead(i+1);

                      }
            
            
                      else{
                  
                      resolve(items);
                  
                      }
               } 
            
            mainhead(0);

       
      }      
   });
 });


}
 

Apify.main(async () => {

    

    const data = await scrape();
    
    
    await Apify.pushData(data);
  
  });

