.ps2

.open "dump\dirty\MAP\M_CMN.BIN", 0x38D580

; Game menu text sizes/positions
; Main
; Day counter 
.org 0x00450230
	.word 128,76,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 16,16,16,16 ; font x-scale, y-scale, x-spacing, y-spacing
; Day of the week
.org 0x00450260
	.word 240,76,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 16,16,16,16 ; font x-scale, y-scale, x-spacing, y-spacing
; Time of the day
.org 0x00450290
	.word 336,76,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 16,16,16,16 ; font x-scale, y-scale, x-spacing, y-spacing
; Weather
.org 0x004502C0
	.word 432,76,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 16,16,16,16 ; font x-scale, y-scale, x-spacing, y-spacing
.org 0x003EAB30
	addiu a2,zero,0x58 ; Player condition bg graphic width
; Inventory
; 'Equiping Items'  handled in elf
; Item names
.org 0x00451300
	.word 20,20,20,20 ; font x-scale, y-scale, x-spacing, y-spacing
.org 0x003F1744
	addiu v1,s1,0x7D ; y-spacing between strings
; Item description at the bottom
.org 0x00451320
	.word 68,342,22,3 ; x-pos, y-pos, num of chars, num of lines
	.word 18,18,18,23 ; font x-scale, y-scale, x-spacing, y-spacing
; 'Sort Inventory' prompt
.org 0x00451350
	.word 62,63,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 22,22,22,22 ; font x-scale, y-scale, x-spacing, y-spacing
; 'Sort Inventory' choices
.org 0x00451380
	.word 184,192,20,1 ; x-pos, y-pos, num of chars, num of lines
	.word 20,20,20,20 ; font x-scale, y-scale, x-spacing, y-spacing
.org 0x004513CC
	.word -16 ; 'Cancel' offset
; Map screen
; Normal map
.org 0x00453020
	.word 40,334,40,3 ; x-pos, y-pos, num of chars, num of lines
	.word 18,18,18,26 ; font x-scale, y-scale, x-spacing, y-spacing
; Full map
.org 0x00453070
	.word 40,334,40,3 ; x-pos, y-pos, num of chars, num of lines
	.word 18,18,18,26 ; font x-scale, y-scale, x-spacing, y-spacing

.close
