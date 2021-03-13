# **Installing libpostal on Windows**
------
###### (Libpostal only works on x64 Windows machines.)

1. Install [msys2](http://msys2.org)
    * Follow the installation instructions exactly,
    * At the current time, these are:
        * `pacman -Syu` in MSYS MINGW 64-bit shell
        * `pacman -Su` in MSYS2 MSYS shell
----
2. Launch a shell using the `MSYS2 MingW 64-bit` start menu option.
3. Punch in the following lines:
    * `pacman -S autoconf automake curl git make libtool gcc mingw-w64-x86_64-gcc`
    * `git clone https://github.com/openvenues/libpostal`
    * `cd libpostal`
    * `./bootstrap.sh`
    * `./configure --datadir=/c`
        * ###### (Here /c stands for C: it will automatically create C:/libpostal , occupies a few GB of space feel free to change dir)
----
4. Before continuing, we need to change a few files. 
		###### Keep the `MSYS2 MingW 64-bit` shell open.
    * Go to your msys installation folder -> home -> user (PC name) -> libpostal,
        * ###### example path: `"C:\msys64\home\[User]\libpostal\libpostal.def"`
    * Open libpostal.def in your preffered text editor and replace it's contents with those found [after clicking this link.](https://raw.githubusercontent.com/openvenues/libpostal/216c947e37cd3d885b2a29b5b330406b7df739a4/libpostal.def)
        * ###### Remember to save the file.
    * From the same libpostal folder navigate to -> src -> klib
        * ###### example path: `"C:\msys64\home\[User]\libpostal\src\klib\drand48.h"`
	* Here you will have to change these lines:
		*  `unsigned short _rand48_seed[3];`
		*  `unsigned short _rand48_mult[3];`
		*  `unsigned short _rand48_add;`
		*  to:
		*  `//unsigned short _rand48_seed[3];`
		*  `//unsigned short _rand48_mult[3];`
		*  `//unsigned short _rand48_add;`
		* ###### Remember to save the file.
----
5. Returning to `MSYS2 MingW 64-bit` punch in these lines:
    * `make`
    * `make install`
----
6.
    * In the msys installation folder -> home -> user (PC name) -> libpostal:
        * ###### example path: `"C:\msys64\home\[User]\libpostal\libpostal.def"`
    * create a new folder named `headers`
	* inside the new folder named headers create a new folder named 'libpostal'
    * Copy libpostal.h from msys installation folder -> mingw64 -> include -> libpostal:
        * ###### example path:`"C:\msys64\mingw64\include\libpostal\libpostal.h"`
    * place it in the last created `headers\libpostal\` folder
        * ###### example path:`"C:\msys64\home\[User]\libpostal\headers\libpostal\"`
----
7.
    * Start a command prompt which has access to the Microsoft toolchain. 
        * ###### This can be done by e.g. installing the [Windows 10 SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk) and then running the ``x64 Native Tools Command Prompt`` 
        * ###### You will also need Microsoft Visual C++ Build Tools. [Here's a direct download link.](https://go.microsoft.com/fwlink/?LinkId=691126)
    * Assuming your python and msys are installed in standard locations, follow these steps to build + install postal:

```
cd "C:\msys64\home\[User]\libpostal\"

"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.28.29333\bin\Hostx64\x64\lib.exe" /def:libpostal.def /out:postal.lib /machine:x64

"C:\Users\[User]\AppData\Local\Programs\Python\Python37\Scripts\pip.exe" install postal --global-option=build_ext --global-option="-IC:\msys64\home\[User]\libpostal\headers" --global-option="-LC:\msys64\home\[User]\libpostal" 

copy src\.libs\libpostal-1.dll "C:\Users\[User]\AppData\Local\Programs\Python\Python37\Lib\site-packages\postal\libpostal.dll"
```