# Flask Website 

This is one of the first websites I built. It was early 2019. The purpose of it was to make large volumes of data available (>20TB). Data was stored on a personal server with Gigabit symmetric internet. However, a port could not be opened on that network, so I made a weird way of doing it. 

Conceptually went: 


Order -> website -> order saved in file


server -> ssh into website -> grab order log -> process order -> push to Google Cloud


website -> searches for key in google cloud -> if it finds it process order -> delete from cloud


Overhead for data storage was virtually 0 (aside from the hardware which was old equipment and some easy store HDD). Query times were also pretty slow. but hey, beats spending 3000/mo on storage. 
