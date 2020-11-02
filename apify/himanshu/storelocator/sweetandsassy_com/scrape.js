const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var base_url = 'https://www.sweetandsassy.com';

 var url = 'https://www.sweetandsassy.com/locations/' ;

 async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
    
        const $  =cheerio.load(html);
        var items=[];
        var main = $('.results').children('li');

        
      //  console.log(main.length);

      function mainhead(i)

      {
          if(main.length>i)

              {

          var obj = main.eq(i);
          var address_tmp = obj.find('address').html().trim();
          var address_tmp1 = address_tmp.split('<br>');

          if(address_tmp1.length == 2){
            
            var address = address_tmp1[0].trim().replace('&#xA0','').replace(';','');
            var city_tmp = address_tmp1[1].replace(/<[^>]*>/g, '').trim().split(',');
            var city = city_tmp[0];
            var state_tmp = city_tmp[1].split(' ');
            var state = state_tmp[1].replace('.','');
            var zip = state_tmp[2];
             
             

          }

         else if(address_tmp1.length == 1){
             
            var address_tmp = obj.find('address').text().trim();
            var address = '<MISSING>';
            var city_tmp = address_tmp.split(',');
            var city = city_tmp[0];
            var state_tmp = city_tmp[1].split(' ');
            var state = state_tmp[1].replace('.','');
            var zip = state_tmp[2];
           

          }

         

          

          var latitude = obj.attr('data-latitude');

          var phone = obj.find('.bottom').find('a').text().trim();
          var longitude = obj.attr('data-longitude');
          var store_number = obj.attr('data-zip');
          var location_name = obj.attr('data-title');
          var link_tmp = obj.attr('data-href');
          var link = base_url+link_tmp;
          

          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
             
                const $  =cheerio.load(html);
                

                var hour_tmp = $('.search-area').find('.hours-detail').text().replace(/\s/g,'').trim();
                if (hour_tmp!=''){
                  var hour = $('.search-area').find('.hours-detail').text().replace(/\s/g,'').trim();
                }
                else
                {
                  var hour = '<MISSING>'
                }


           


                items.push({  

                  locator_domain: 'https://www.sweetandsassy.com', 
      
                  location_name: location_name, 
      
                  street_address: address,
      
                  city: city, 
      
                  state: state,
      
                  zip:  zip,
      
                  country_code: 'US',
      
                  store_number: store_number,
      
                  phone: phone,
      
                  location_type: '<MISSING>',
      
                  latitude: latitude,
      
                  longitude: longitude, 
      
                  hours_of_operation: hour,
                  
                  page_url:link}); 

                 
      
                  mainhead(i+1);
              

            }

          });
              


         
          
 
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
