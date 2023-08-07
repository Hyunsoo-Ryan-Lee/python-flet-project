import mysql.connector

# CONECTION TO DB
lottoDB = mysql.connector.connect(
        host="localhost",
        user="hyunsoo",
        password="150808",
        database="flet"
        )

    
# create table lotto(id int(11) NOT NULL AUTO_INCREMENT, conntime datetime NOT NULL, ipaddr varchar(128) NOT NULL, number varchar(128) NOT NULL, gamecnt int(11) NOT NULL, PRIMARY KEY (id));