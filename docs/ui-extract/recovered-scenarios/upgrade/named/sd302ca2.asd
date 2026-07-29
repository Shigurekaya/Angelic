;! clipleft=0 cliptop=0 clipwidth=1125 clipheight=675
*loop
; 1
	@clip left=0 top=0
	@wait time=500
; 2
	@clip left=0 top=675
	@wait time=500
@jump target=*loop
