def defineHeader():
    Header = " !\n"*5 + "version 15.2\n" + "service timestamps debug datetime msec\n" + "service timestamps log datetime msec\n" + "!\n" + "hostname R1\n" + "!\n" + "boot-start-marker\n" +"boot-end-marker\n" + "!\n"*3 + "no aaa new-model\n" + "no ip icmp rate-limit unreachable\n" + "ip cef\n" + "!\n"*6 +"no ip domain lookup\n"+ "no ipv6 cef\n"+ "!\n"*2 +"multilink bundle-name authenticated\n" +"!\n"*9 +"ip tcp synwait-time 5\n" + "!\n"*12
    return Header

def defineFin():
    Fin = "!\n" + "ip forward-protocol nd\n"+"!\n"*2 +"no ip http server\n"+"no ip http secure-server\n"+"!\n"*4 +"control-plane\n"+"!\n"*2+"line con 0\n"+"exec-timeout 0 0\n"+"privilege level 15\n" + "logging synchronous\n" + "stopbits 1 \n" +"line aux 0\n" +"exec-timeout 0 0\n" +"privilege level 15\n" + "logging synchronous\n"+"stopbits 1\n"+"line vty 0 4\n"+"login\n" + "!\n" *2 +"end"
    return Fin

def add_str_to_lines(f_name, str_to_add):
    with open(f_name, "w") as f:
            f.write(str_to_add)
            return str_to_add

if __name__ == "__main__":
    defineFin()
    defineHeader()
    str_to_add = " !\n"*5 + "version 15.2\n" + "service timestamps debug datetime msec\n" + "service timestamps log datetime msec\n" + "!\n" + "hostname R1\n" + "!\n" + "boot-start-marker\n" +"boot-end-marker\n" + "!\n"*3 + "no aaa new-model\n" + "no ip icmp rate-limit unreachable\n" + "ip cef\n" + "!\n"*6 +"no ip domain lookup\n"+ "no ipv6 cef\n"+ "!\n"*2 +"multilink bundle-name authenticated\n" +"!\n"*9 +"ip tcp synwait-time 5\n" + "!\n"*12
    print(str_to_add)
    f_name = "file.txt"
    with open(f_name, "w") as f:
        f.write(str_to_add)


