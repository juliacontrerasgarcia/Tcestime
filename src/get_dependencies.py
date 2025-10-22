#! /usr/bin/env python3

import os

def get_dependencies():
    critic2=os.popen("which critic2").read()
    if critic2=="":
        critic2=input("If you have critic2 already installed, please provide the path (otherwise press ENTER): ")

    if critic2=="":
        yn = input("You do not have critic2 currently installed. Do you wish to install it? [y/n] ")
        if yn.lower() == "n": 
            print("TcESTIME cannot proceed without the installation of critic2.")
            exit()
        elif yn.lower() == "y":
            direc = input("Where do you want to install critic2? Press enter to install in /opt : ")
            if direc == "" :
                dir_critic2 = "/opt"
            else:
                dir_critic2 = direc
            print("Installing critic2 in ", dir_critic2)
            dir_here = os.popen("pwd").read()[:-1]
            wget = os.system("wget -P "+dir_critic2+" 'https://github.com/aoterodelaroza/critic2/archive/refs/tags/1.1stable.tar.gz'")
            if wget == 0:
                os.chdir(dir_critic2)
                os.system("tar -xzf 1.1stable.tar.gz")
                #critic2_path = os.path.join(dir_critic2, "critic2-1.1stable")
                os.chdir("critic2-1.1stable")
                #os.system("pwd")
                os.system("autoreconf -i")
                os.system("./configure")

            else:
                wget = os.system("sudo wget -P "+dir_critic2+" 'https://github.com/aoterodelaroza/critic2/archive/refs/tags/1.1stable.tar.gz'")
                os.chdir(dir_critic2)
                #os.system("pwd")
                os.system("sudo tar -xzf 1.1stable.tar.gz")
                #critic2_path = os.path.join(dir_critic2, "critic2-1.1stable")
                os.chdir("critic2-1.1stable")
                #os.system("pwd")
                os.system("sudo autoreconf -i")
                os.system("sudo ./configure")

                
            os.system("sudo make")
            os.system("sudo make install")
            critic2 = os.popen("which critic2").read()
            os.chdir(dir_here)
            print("Current critic2: ", critic2)
        else:
            print("Please answer yes (y) or no (n).")
    else:
        print("Current critic2: ", critic2)
