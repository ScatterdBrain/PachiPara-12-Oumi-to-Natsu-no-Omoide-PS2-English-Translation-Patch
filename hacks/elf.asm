.ps2

.open "dump\dirty\SLPS_255.74", 0xFFD00

; Code cave in place of memory card message strings.
.org 0x002D7E28
	nop
.area 0x920,0x00
	; This is a copy of a function at 0x0015DDA0 modified to add a vwf functionality
	; Game calls this function 3 times for every character on screen
	; but only one of those calls affects the spacing after characters
	; This modified function will be used in places of that call
	@vwf_hack:
		lw a3,-0x7DC8(gp)
		lui v0,0x002F
		lw a2,-0x3190(v0)
		addiu a1,zero,0x2
		lw v1,0x20(a3)
		beq a2,a1,@@branch1
		daddu v0,v1,zero
		addiu a1,zero,0x1
		beq a2,a1,@@branch2
		nop 
		beq a2,zero,@@branch3
		nop 
		beq zero,zero,@@branch4
		nop
		@@branch3:
			slti at,a0,0x0080 ; if not ASCII
			beq at,zero,@@branch5
			nop 
			lw at,0x48(a3) ; keep a0 which has an ASCII value and use at instead
			bne at,zero,@@branch5 ; a0 to at
			nop 
			lw at,0x4C(a3) ; a0 to at
			beq at,zero,@@branch5 ; a0 to at
			nop 
			;original code just halves ASCII char width
				;bgez v1,@@branch5
				;sra v0,v1,0x01
				;addiu v0,v1,0x1
				;sra v0,v0,0x01
				;beq zero,zero,@@branch4
				;nop
			; multiply font size by table value then divide by 24 (size of char bitmap)
			lui v0, hi(org(@vwf_table))
			addu v0,v0,a0
			lb v0,lo(org(@vwf_table))-0x20(v0)
			mult v0,v0,v1
			ori a0,zero,0x18
			div v0,a0
			beq zero,zero,@@branch5
			mflo v0
		@@branch2:
			lw a0,0x4C(a3)
			beq a0,zero,@@branch5
			nop 
			bgez v1,@@branch5
			sra v0,v1,0x01
			addiu v0,v1,0x1
			sra v0,v0,0x01
			beq zero,zero,@@branch4
			nop
		@@branch1:
			ori a1,zero,0xA3A1
			slt a1,a0,a1
			bne a1,zero,@@branch6
			nop 
			ori at,zero,0xA3FF
			slt at,a0,at
			beq at,zero,@@branch6
			nop 
			lw a1,0x4C(a3)
			beq a1,zero,@@branch6
			nop 
			lui a1,0x002F
			addiu a2,zero,0x1
			lw a1,-0x318C(a1)
			beq a1,a2,@@branch6
			nop 
			bgez v1,@@branch6
			sra v0,v1,0x01
			addiu v0,v1,0x1
			sra v0,v0,0x01
			beq zero,zero,@@branch6
			nop 
			slti at,a0,0x0080
		@@branch8:
			beq at,zero,@@branch7
			nop 
			lw a1,0x4C(a3)
			beq a1,zero,@@branch7
			nop 
			bgez v1,@@branch7
			sra v0,v1,0x01
			addiu v0,v1,0x1
			sra v0,v0,0x01
		@@branch7:
			lw a1,-0x7FB8(gp)
			bne a0,a1,@@branch5
			nop 
			lw a0,0x4C(a3)
			beq a0,zero,@@branch5
			nop 
			bgez v1,@@branch4
			sra v0,v1,0x01
			addiu v0,v1,0x1
			sra v0,v0,0x01
		@@branch4:
			beq zero,zero,@@branch5
			nop 
		@@branch6:
			lui a1,0x002F
			addiu a2,zero,0x1
			lw a1,-0x318C(a1)
			beq a1,a2,@@branch7
			nop 
			beq zero,zero,@@branch8
			slti at,a0,0x0080
		@@branch5:
			jr ra
			nop
		; Values in this table tell width of char bitmap in pixels
		; table indexed by ASCII value of a char
		@vwf_table:
			;         !  "  #  $  %  &  '  (  )  *  +  ,  -  .  / 
			.byte  8, 8,12,14,14,14,14, 6,12,12,16,16, 8,16, 8,16
			;      0  1  2  3  4  5  6  7  8  9  :  ;  <  =  >  ?
			.byte 14,14,14,14,14,14,14,14,14,14, 8, 8,16,16,16,16
			;      @  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O
			.byte 16,14,14,14,14,14,14,14,14, 6,12,14,14,14,14,14
			;      P  Q  R  S  T  U  V  W  X  Y  Z  [  \  ]  ^  _
			.byte 14,14,14,14,14,14,14,14,14,14,14,12,14,12,14,16
			;      `  a  b  c  d  e  f  g  h  i  j  k  l  m  n  o
			.byte 12,14,14,14,14,14,14,14,14, 6,12,14, 6,14,14,14
			;      p  q  r  s  t  u  v  w  x  y  z  {  |  }  ~ 7F
			.byte 14,14,12,12,14,14,14,14,14,14,14,13,14,13,16,12
.endarea
	nop

; Jumps to VWF routine
.org 0x0015F550
	jal @vwf_hack
.org 0x0015F668
	jal @vwf_hack

; Text boxes positions/sizes
; TODO!!!
; Dialogue window
.org 0x00285640
.word 80,352,3,27 ; x-pos, y-pos, num of lines (height), num of chars (width)
.word 18,18,18,18 ; font x-scale, y-scale, x-spacing, y-spacing
; Cutscene choices box
.org 0x002856D0
.word 32,80,5,21 ; x-pos, y-pos, num of lines (height), num of chars (width)
.word 18,18,18,18 ; font x-scale, y-scale, x-spacing, y-spacing

; Memory card messages fixes
.org 0x001C6D10
	or a0,zero,zero ; Sets byte that converts ASCII chars to full width SJIS for memory card messages.
.org 0x001C6D18
	ori a0,zero,0x1 ; Enables VWF for memory card messages.

; Save/Load screen fixes
; Swap '[number] day' string to 'day [number]'
.org 0x002DDE98
.ascii "%s%3d"
.org 0x00259020
	daddu a3,s0,zero
	daddu a2,v0,zero
; Text positions/sizes
.org 0x00258E5C
	addiu s1,v0,0x6B ; y-pos of all text
.org 0x002C0570
	.word 18,18,18,28 ; font x-scale, y-scale, x-spacing, y-spacing
.org 0x00258FF4
	addiu v1,zero,0x152 ; 'day [number]' x-pos
.org 0x00259064
	addiu v1,zero,0x1BA ; day of the week x-pos
.org 0x002590C8
	addiu v1,zero,0x214 ; time of the day x-pos
.org 0x002591FC
	addiu a0,zero,0x1E5 ; number of balls x-pos

; Pointers to string terminator
.org 0x0028452C :: .word 0x002D7E1C
.org 0x0028454C :: .word 0x002D7E1C
.org 0x00284560 :: .word 0x002D7E1C
.org 0x0028457C :: .word 0x002D7E1C
.org 0x00284590 :: .word 0x002D7E1C
.org 0x002845BC :: .word 0x002D7E1C
.org 0x002845DC :: .word 0x002D7E1C
.org 0x00284654 :: .word 0x002D7E1C
.org 0x002846AC :: .word 0x002D7E1C
.org 0x00284704 :: .word 0x002D7E1C
.org 0x00284750 :: .word 0x002D7E1C
.org 0x0028476C :: .word 0x002D7E1C
.org 0x00284790 :: .word 0x002D7E1C
.org 0x002847AC :: .word 0x002D7E1C
.org 0x002847CC :: .word 0x002D7E1C
.org 0x0028489C :: .word 0x002D7E1C
.org 0x002848BC :: .word 0x002D7E1C
.org 0x002848E0 :: .word 0x002D7E1C
.org 0x00284910 :: .word 0x002D7E1C

.close