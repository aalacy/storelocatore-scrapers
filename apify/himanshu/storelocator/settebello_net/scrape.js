const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
 
 var tmp_url ='http://settebello.net/';
var url = 'http://settebello.net/Locations-Henderson.php';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        
        var main = $('#navSub').find('ul').find('li');
        function mainhead(i)

        {
            if(main.length>i)

                {
          var link = tmp_url+$('#navSub').find('ul').find('li').eq(i).find('a').attr('href');
          var location_name  =$('#navSub').find('ul').find('li').eq(i).find('a').text();
          
          
          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
              const $  =cheerio.load(html);
                        var phone_tmp = $('.col2').find('p').find('a').text().split('F:');
                        var phone = phone_tmp[0].replace('P: ','');
                        var hour = $('.col1').text().trim().replace('Hours','').replace(/\t/g, '').replace(/\n/g, '');
                        var latitude_tmp = $('iframe').attr('src');
                        var latitude_tmp1 = latitude_tmp.split('ll');
                        var latitude_tmp2 = latitude_tmp1[latitude_tmp1.length-1];
                        var latitude_tmp3 = latitude_tmp2.split('&spn');
                              if(latitude_tmp3.length == 2){
                                var latitude_tmp4 = latitude_tmp3[0];
                                var latitude_tmp5 = latitude_tmp4.split(',');
                                
                                var latitude = latitude_tmp5[0].replace('=','');
                              var longitude = latitude_tmp5[1].replace('=','');

                              }
                              else if(latitude_tmp3.length == 1){
                                var latitude = '<MISSING>';
                                var longitude = '<MISSING>';

                              }
               
             
               
                        var tmp_add = $('.col2').find('p').html();
                        var tmp_add1 = tmp_add.split('<br>');
                        var address = tmp_add1[0];
                        var city_tmp = tmp_add1[1].trim();
                        var city_tmp1 =city_tmp.split(',');
                            if(city_tmp1.length ==2){
                              var city = city_tmp1[0];
                              var state_tmp = city_tmp1[1].split(' ');
                              var state = state_tmp[1];
                              var zip = state_tmp[2];
                              
                            }
                            else if(city_tmp1.length ==1){
                              
                              var state_tmp = city_tmp1[0].split(' ');
                              var city = city_tmp1[0];
                              var state = state_tmp[1];
                              var zip = state_tmp[2];
                

                             }
              
             
           
                             items.push({
                              locator_domain : 'http://settebello.net/',
                              location_name : location_name,
                              street_address : address,
                              city:city,
                              state:state,
                              zip:zip,
                              country_code: 'US',
                              store_number:'<MISSING>',
                              phone:phone,
                              location_type:'settebello',
                              latitude:latitude,
                              longitude :longitude,
                              hours_of_operation:hour
                              
                              });  
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