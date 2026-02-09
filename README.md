# PachiPara-12-English-Translation
An English translation project for "PachiPara 12: Ōumi to Natsu no Omoide" [SLPS-25574] PS2 game developed by IREM.

## Tools used:
* [PCSX2](https://pcsx2.net/) - Debugging.
* [QuickBMS](https://aluigi.altervista.org/quickbms.htm) - unpacking of .DAT files with disaster_report.bms script.

## Credits:
* **GXZ95** - Translation

## How to:
### Working With Text Files:
#### Step 1:
Import csv text file into spreadsheet editor of your choice using these settings.\
<img src="misc/csv_import.webp"/>

#### Step 2:
Put desired text into "e_string" field.\
<img src="misc/csv_spreadsheet.webp"/>

#### Step 3:
Export edited file using these settings.\
<img src="misc/csv_export.webp"/>

#### Fields Explanation:
* block - which block of text particular string resides.
* j_offset - address of original string.
* j_string - original string.
* e_string - translated string
* pointer - address of pointer to the string.
