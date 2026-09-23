.ps2

.open "dump\dirty\SLPS_255.74", 0x0 ; Open file and don't use memory offset

; Use this as a template
; 03061 ; Name of the texture to keep track
; Background ; Description of what sprite it is
.org 0x001B19F0 + 2; offset from sprite_dat.csv +2 to skip writing texture id
	; Write sprite data from sprite_data.csv
	@@width			equ 408 ; width
	@@height		equ 204 ; height
	@@x_start		equ 0	; x_start
	@@y_start		equ 0	; y_start
	@@x_screen_pos	equ 216	; x_scrn_off
	@@y_screen_pos	equ 216 ; y_scrn_off
; Portion below should be the same for all sprites
	.halfword @@width,@@height
	.halfword 0 ; zero separator
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start ; x_end, y_end. Just add width to x_start and height to y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Ball graphic
.org 0x001B1A50 + 2
	@@width			equ 32
	@@height		equ 32
	@@x_start		equ 120 + 4 ; moved x_start 4 pixels to the right because I made outline wider
	@@y_start		equ 232
	@@x_screen_pos	equ 0
	@@y_screen_pos	equ 0
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Outline
.org 0x001B1AB0 + 2
	@@width			equ 120 + 4 ; made outline 4 pixels wider to get some more space
	@@height		equ 32 ; can't really change height without big code changes
	@@x_start		equ 0
	@@y_start		equ 232
	@@x_screen_pos	equ 0
	@@y_screen_pos	equ 0
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Code changes ; Some sprites will need extra work to move them around
.org 0x00250A94 - 0xFFD00
	addiu a0,a0,0x11A ; outline x-offset
.org 0x002509F4 - 0xFFD00
	addiu v1,zero,0xEE ; ball x-offset 1st row
.org 0x00250A20 - 0xFFD00
	addiu v1,zero,0x176 ; ball x-offset 2nd row
.org 0x00250A4C - 0xFFD00
	addiu v1,zero,0x1FE ; ball x-offset 3rd row

; 03075
; Atlantis
.org 0x001B5C50 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 268
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Lagoon
.org 0x001B5CB0 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 32
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 300
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Treasure
.org 0x001B5D10 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 64
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 332
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos
	
; Sam Bikini
.org 0x001B5D70 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 96
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 364
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Sam Wetsuit
.org 0x001B5DD0 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 128
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 396
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Sandy Beach
.org 0x001B5E30 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 160
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 268
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Classroom
.org 0x001B5E90 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 192
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 300
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Street Corner
.org 0x001B5EF0 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 0
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 332
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Pachinko Parlor
.org 0x001B5F50 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 32
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 364
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Palm Tree
.org 0x001B5FB0 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 64
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 268
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Bubbles
.org 0x001B6010 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 96
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 300
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Beach Umbrella
.org 0x001B6070 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 128
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 332
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; Ghost
.org 0x001B60D0 + 2
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 160
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 364
	.halfword @@width,@@height
	.halfword 0
	.halfword @@x_start,@@y_start
	.halfword @@width + @@x_start, @@height + @@y_start
	.halfword @@x_screen_pos,@@y_screen_pos

; ????? uses previous sprites positions, so no changes needed

.close ; Close file
