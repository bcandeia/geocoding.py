# coding=utf-8
#BrunaCandeia
#Github https://github.com/bcandeia

from time import sleep

#Pelo Google Maps

endereco = open("enderecos.txt")
for line in endereco:
    sleep(2)
    from geopy.geocoders import GoogleV3
    geolocator = GoogleV3(api_key=' AIzaSyDMAvSZhXqjFrHHwJyAVWckGuluXaPWzPY')
    location = geolocator.geocode(str(line), timeout=100)
    if location:
        lat=location.latitude
        lon=location.longitude
        coord_finais = open("coord_finais.txt", "a")
        coord_finais.write("Endereco: " + line + " ") 
        coord_finais.write("Coordenadas: " + str((location.latitude, location.longitude)) + "\n")
        coord_finais.close()
        print((location.latitude, location.longitude))
    else:
        lat = None
        lon = None
        coord_finais = open("coord_finais.txt", "a")
        coord_finais.write("Endereco: " + line + " ") 
        coord_finais.write("Coordenadas: Não encontradas")
        coord_finais.close()
        print("Coordenadas: Não encontradas")