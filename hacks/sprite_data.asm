.ps2

.open "dump\dirty\SLPS_255.74", 0x0 ; Open file and don't use memory offset

@memory_offset equ 0xFFD00

.macro write_sprite_data,width,height,x_start,y_start,x_end,y_end,x_screen_pos,y_screen_pos
	.skip 2 ; skip writing texture id
	.halfword width,height
	.skip 2 ; zero separator
	.halfword x_start,y_start
	.if x_end == 0 || y_end == 0 ; If either endpoint = 0 just add width to x_start and height to y_start
		.halfword width + x_start, height + y_start
	.else ; Else add new endpoints to start points
		.halfword x_start + x_end, y_start + y_end
	.endif
	.halfword x_screen_pos,y_screen_pos
.endmacro

; Use this as a template
; 03061 ; Name of the texture to keep track
; Background ; Description of what sprite it is
.org 0x001B19F0; offset from /graphics/tm2/sprite_data.csv
	; width and height of the sprite as it will be rendered on screen
	@@width			equ 408 ; width
	@@height		equ 204 ; height
	; start point of the sprite on texture sheet
	@@x_start		equ 0	; x_start
	@@y_start		equ 0	; y_start
	; end point of the sprite on texture sheet
	@@x_end			equ 0	; x_end
	@@y_end			equ 0	; y_end
	; Usually endpoints would be equal to width + x_start and height + y_start.
	; So, if we write correct width and height values above, we can just leave endpoints at 0.
	; Then the macro will take care of this addition
	; However, if we want to scale sprite to an arbitrary size, we can write new width and height values.
	; Then write actual width and height as values for end points.
	; ex. @@width equ 204 :: @@height equ 102 :: @@x_end equ 408 :: @@y_end equ 204)
	; Example above would make this sprite render at 0.5x scale.
	@@x_screen_pos	equ 216	; x_scrn_off
	@@y_screen_pos	equ 216 ; y_scrn_off
; Portion below should be the same for all sprites
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Ball graphic
.org 0x001B1A50
	@@width			equ 32
	@@height		equ 32
	@@x_start		equ 120 + 4 ; moved x_start 4 pixels to the right because I made outline wider
	@@y_start		equ 232
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 0
	@@y_screen_pos	equ 0
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Outline
.org 0x001B1AB0
	@@width			equ 120 + 4 ; made outline 4 pixels wider to get some more space
	@@height		equ 32 ; can't really change height without big code changes
	@@x_start		equ 0
	@@y_start		equ 232
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 0
	@@y_screen_pos	equ 0
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Code changes ; Some sprites will need extra work to move them around
.headersize @memory_offset ; Change offset to use memory addresses
.org 0x00250A94
	addiu a0,a0,0x11A ; outline x-offset
.org 0x002509F4
	addiu v1,zero,0xEE ; ball x-offset 1st row
.org 0x00250A20
	addiu v1,zero,0x176 ; ball x-offset 2nd row
.org 0x00250A4C
	addiu v1,zero,0x1FE ; ball x-offset 3rd row
.headersize 0x0 ; Return offset to 0


; 03075
; Atlantis
.org 0x001B5C50
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 0
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 268
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Lagoon
.org 0x001B5CB0
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 32
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 300
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Treasure
.org 0x001B5D10
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 64
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 332
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos
	
; Sam Bikini
.org 0x001B5D70
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 96
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 364
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Sam Wetsuit
.org 0x001B5DD0
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 128
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 300 - 4
	@@y_screen_pos	equ 396
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Sandy Beach
.org 0x001B5E30
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 160
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 268
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Classroom
.org 0x001B5E90
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 0
	@@y_start		equ 192
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 300
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Street Corner
.org 0x001B5EF0
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 0
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 332
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Pachinko Parlor
.org 0x001B5F50
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 32
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 436 - 4
	@@y_screen_pos	equ 364
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Palm Tree
.org 0x001B5FB0
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 64
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 268
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Bubbles
.org 0x001B6010
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 96
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 300
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Beach Umbrella
.org 0x001B6070
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 128
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 332
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; Ghost
.org 0x001B60D0
	@@width			equ 88
	@@height		equ 32
	@@x_start		equ 88
	@@y_start		equ 160
	@@x_end			equ 0
	@@y_end			equ 0
	@@x_screen_pos	equ 572 - 4
	@@y_screen_pos	equ 364
	write_sprite_data @@width,@@height,@@x_start,@@y_start,@@x_end,@@y_end,@@x_screen_pos,@@y_screen_pos

; ????? uses previous sprites positions, so no changes needed

.close ; Close file
