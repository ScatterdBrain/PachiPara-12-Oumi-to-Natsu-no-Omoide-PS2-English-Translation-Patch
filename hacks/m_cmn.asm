.ps2


.open "dump\dirty\MAP\M_CMN.BIN", 0x38D580

; Code cave in place of food place name strings. They'll end up elsewhere during reinsertion anyway.
.org 0x00462268
.area 0x184,0x00
	; Hacks used while entering player name.
	@is_valid_ascii:
		lw v1,0x1C(s1)
		addu a2,a2,v1 ; add cursor column position to counter
		lw v1,0x20(s1)
		@@loop_start: ; loop over cursor row position while adding max-columns to counter
			beq v1,zero,@@loop_exit
			addiu v1,v1,-0x1
			beq zero,zero,@@loop_start
			addiu a2,a2,0xB
		@@loop_exit:
		lw v1,0x24(s1)
		beq v1,zero,@@branch1 ; if cursor on second page add max rows*columns to counter
		lui v1,hi(org(@sjis_ascii_table))
		addiu a2,a2,0x37
		@@branch1:
			slti v0,a2,0x004D
			beq v0,zero,@@non_valid_return ; counter out of LUT range 
			nop 
			addu a2,a2,v1
			lb a2,lo(org(@sjis_ascii_table))(a2)
			bne a2,zero,@@valid_char ; if a2 not 0x00 then is valid char
			nop
		@@non_valid_return:	
			j 0x0040CF20 ; return code that runs if you press on empty space
			nop
		@@valid_char:
			lw a1,0x10(a0)
			slti v1,a1,0x0004
			beq v1,zero,@@first_name ; check if name cursor at family name or first name
			nop
			@@family_name:
				addiu v1,s1,0x34
				@@loop1: ; find 0x00 byte to write ASCII to
					lb v0,0x0(v1)
					bne v0,zero,@@loop1
					addiu v1,v1,0x1
				sb a2,-0x1(v1)
				sub v1,v1,s1
				addiu v1,v1,-0x34
				srl v1,v1,0x01
				or v0,v1,zero
				j 0x0040CF68
				sw v1,0x30(a0)
			@@first_name:
				addiu v1,s1,0x44
				@@loop2: ; same as @@loop1 above
					lb v0,0x0(v1)
					bne v0,zero,@@loop2
					addiu v1,v1,0x1
				sub v0,v1,s1
				sltiu v0,v0,0x004D		; zero out a2 if we at the end of the string
				beql v0,zero,@@branch2	; this is different behaviour from the original
				or a2,zero,zero			; original just overwrites last character
				@@branch2:				; but here we do nothing at all esentially
				sb a2,-0x1(v1)			; if we want to allow mixing S-JIS with ASCII
				sub v1,v1,s1			; i think this is the best way?
				addiu v1,v1,-0x44
				srl v1,v1,0x01
				or v0,v1,zero
				j 0x0040CFB0
				sw v1,0x40(a0)
	; conversion table for S-JIS English chars to ASCII during name entry
	; table indexed by row-column-page position of the cursor
	@sjis_ascii_table:
		.byte 'A','B','C','D','E','F','G','H','I','J', 0 ,'K','L','M','N','O'
		.byte 'P','Q','R','S','T', 0 ,'U','V','W','X','Y','Z', 0 , 0 , 0 , 0 
		.byte  0 ,'a','b','c','d','e','f','g','h','i','j', 0 ,'k','l','m','n'
		.byte 'o','p','q','r','s','t', 0 ,'u','v','w','x','y','z', 0 , 0 , 0 
		.byte  0 , 0 ,'0','1','2','3','4','5','6','7','8','9', 0 , 0 , 0 , 0 
	@name_space_sep:
		addu a0,a0,a1
		slti a0,a0,0x0008
		beq a0,zero,@@pass ; if all 16 bytes taken do default
		addiu a1,s0,0x44
		ori a0,zero,0x20
		addiu a1,a1,-0x1
		sb a0,0x0(a1)
		@@pass:
			jal 0x001B9450
			addiu a0,sp,0x20
			j 0x0040CB8C
			nop
.endarea
nop

; Player name entry
.org 0x0040D7D0
.area 0x90,0x00
	; original function shortened + defaulted cursor position to English keyboard
	@@clear_memory_for_name_entry:
		addiu v1,zero,0x1
		sq v1,0x0(a0)
		addiu v1,zero,-0x1
		sw v1,0xC(a0)
		sq zero,0x10(a0)
		sq zero,0x20(a0)
		ori a1,zero,0x8	; Point cursor at English keyboard
		sw a1,0x14(a0)	;
		ori a1,zero,0x4	;
		sw a1,0x18(a0)	;
		sq zero,0x30(a0)
		sq zero,0x40(a0)
		jr ra
		sw zero,0x60(a0)
	; used free space to check if English keyboard to convert S-JIS English to ASCII
	@is_eng_keyboard:
		lw a1,0x18(a0)
		ori v1,zero,0x4
		bne a1,v1,@@not_eng
		lw a1,0x14(a0)
		sll v1,v1,0x01
		bne a1,v1,@@not_eng
		or a2,zero,zero
		@@it_is_eng:
			j @is_valid_ascii
			nop
		@@not_eng:
			j 0x0040CE88
			slti at,a1,0x0005
	; name cursor moves 2-bytes at the time
	; code below sort of a half-ass fix that tied to the way ASCII are typed now
	; cursor still moves 2-bytes, but only if there's 1 S-JIS or 2 ASCII letters
	; so we stay at the same spot with single ASCII char
	@name_cursor_counter:
		lw v1,0x44(s1)
		bnel v1,zero,@@first_name
		lw v1,0x40(s1)
		@@family_name:	
			jr ra
			lw v1,0x30(s1)
		@@first_name:
			jr ra
			addiu v1,v1,0x4
.endarea

; replaced beggining of this function with a jump
; that checks if current keyboard is English
.org 0x0040CE80
	j @is_eng_keyboard
	nop
; Use different counter for name cursor
.org 0x0040C700
	jal @name_cursor_counter
	nop
; Erase WORD not BYTE - family name
.org 0x0040C5EC
	sw zero,0x34(v1)
; Erase WORD not BYTE - first name
.org 0x0040C620
	sw zero,0x3C(v1)
; jump to hack that adds space between family name and first name
; if their combined length less than 16 bytes
.org 0x0040CB80
	lw a0,0x30(s0)
	j @name_space_sep
	lw a1,0x40(s0)
; do not shift name cursor highlight by 2 bytes
; just keep it on either family name or first name
.org 0x0040D3B4
	nop
; 'First'/'Last'/'End' x-spacing
.org 0x0040CCF8
	addiu a0,zero,0x18
; 'First'/'Last' x-pos
.org 0x0040D230
	addiu a0,zero,0x19A
; Really cool idea to give 'End' two possible x-offsets
; but use the same single x-offset for 'First' and 'Last'!
; 'End' x-pos when 'Last'
.org 0x0040D288
	addiu a0,zero,0x1E9
; 'End' x-pos when 'First'
.org 0x0040D2A8
	addiu a0,zero,0x1E9

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
; Shop Screen
.org 0x0045D430
	.word 80,352,26,3 ; x-pos, y-pos, num of chars, num of lines
	.word 20,20,20,22 ; font x-scale, y-scale, x-spacing, y-spacing

.close
