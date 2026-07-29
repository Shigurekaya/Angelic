;! clipleft=0 cliptop=0 clipwidth=1125 clipheight=675
*loop
; 手１
	@clip left=0 top=0
	@wait time=500
; 手２
	@clip left=0 top=675
	@wait time=500
@jump target=*loop
