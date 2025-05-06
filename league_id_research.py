from sleeper_wrapper import User
import time

commish_list = [
    "DerJenser","faxe1984","Holstein","Stendalizer","Lackomat","Stoni","MaryoLarry",
    "jozu96","EkelLenny","donSchlattio","mortadeller","sachsenholly","seku82","MrNilsson",
    "Pandorika","TobiWalonso","uncl3joe","rafiniert","0leMnrs","MatzeLuki","Senturas",
    "ESAChargers","MartinB","Tsubasa37","jUstusj0n4s","lueckenbuesser","game256",
    "JahGibbsMyr","niklasw444","Matos1406","ledanyo","Bummi","miami84","ChrisVii",
    "marvhin23","Fritschi75","Creech3r","Falog","TheGoldenBoy5","Ycke","koti1985",
    "chaefer77"
]

unique_commish_list = list(set(commish_list))
commish_user_ids = [
    '603326865771405312', 
    '762820364672835584', 
    '867544786272460800', 
    '751566194544381952', 
    '862758578077999104', 
    '685764901146263552', 
    '739465979662344192', 
    '646519878408404992', 
    '388753670600163328', 
    '842437747540086784', 
    '756189668307046400', 
    '549968432082165760', 
    '736369538890858496', 
    '475337602711416832', 
    '472327770609807360', 
    '742696879162290176', 
    '700775678882189312', 
    '871161774752358400', 
    '595382602781753344', 
    '859916391497711616', 
    '698638639181172736', 
    '696419424483233792', 
    '643774380593205248', 
    '470366281862737920', 
    '298013498846220288', 
    '989203503744593920', 
    '998202792059727872', 
    '600075246535507968', 
    '460135429803339776', 
    '839949979090030592', 
    '675598189872627712', 
    '740271047152128000', 
    '733450277348331520', 
    '870756923782402048', 
    '589565582072918016', 
    '605826565590294528', 
    '649596615060979712', 
    '646516826129522688', 
    '585507399792627712', 
    '977746984348012544', 
    '699720820305489920'
    ]

for user_id in commish_user_ids:
    user = User(user_id)
    user_data = user.get_all_leagues(sport="nfl", season=2025)
    for league in user_data:
        print(f"\"{league['league_id']}\", # {league['name']}")