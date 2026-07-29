;! clipleft=0 cliptop=0 clipwidth=1125 clipheight=675
*loop
; １
	@clip left=0 top=0
	@wait time=1000
; ２
	@clip left=0 top=675
	@wait time=1000
@jump target=*loop
