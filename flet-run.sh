#!/bin/bash

echo "WHAT APP DO YOU WANT TO START? ENTER THE NUMEBER"
echo "1. LOTTERY SITE"
echo "2. MEMORY GAME"
echo "3. AWS FILE UPLOADER"

read app

if [ $app == "1" ]; then
	echo "LOTTERY SITE START!"
    source /home/ubuntu/Flet-App/flet/bin/activate
    flet run -w /home/ubuntu/Flet-App/python-flet-project/lottery-site/flet_main.py -p 2010
elif [ $app == "2" ]; then
	echo "MEMORY GAME START!"
    source /home/ubuntu/Flet-App/flet/bin/activate
    flet run -w /home/ubuntu/Flet-App/python-flet-project/memory-game/flet_main.py -p 2020
elif [ $app == "3" ]; then
	echo "AWS FILE UPLOADER START!"
    source /home/ubuntu/Flet-App/flet/bin/activate
    flet run -w /home/ubuntu/Flet-App/python-flet-project/photo-uploader/flet_main.py -p 2000
else
	echo "WRONG NUMBER!"
fi