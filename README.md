# PachiPara-12-English-Translation
An English translation project for "PachiPara 12: Ōumi to Natsu no Omoide" [SLPS-25574] PS2 game developed by IREM.

# Usage
Download the repository to your PC then drag and drop your copy of "PachiPara 12" ISO on dump_iso.py script (you will need a ver 2.01 of the game MD5:d4a0ea206a803b2bf6605747248d01f0).
When running the script, type **2** to skip extracting game assets (like graphics and text) so you don't overwrite the ones already in the repo.

## Python dependencies
To run iso rebuilding py script you'll need to install following libraries.
* [PIL](https://pillow.readthedocs.io/en/stable/)
* [imagequant-python](https://github.com/wanadev/imagequant-python)

## Tools used:
* [mkps2iso](https://github.com/N4gtan/mkps2iso) - dumping and rebuilding of iso image.
* [QuickBMS](https://aluigi.altervista.org/quickbms.htm) - unpacking of .DAT files with disaster_report.bms script.
* [PCSX2](https://pcsx2.net/) - Debugging.
* [armips](https://github.com/Kingcom/armips) - MIPS assembler.

## Credits:
* **ScatterBrain** - Hacking, programming.
* **GXZ95** - Translation
