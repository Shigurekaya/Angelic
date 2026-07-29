;! clipleft=0 cliptop=0 clipwidth=1125 clipheight=675
*loop
; はね１
	@clip left=0 top=0
	@wait time=1000
; はね２
	@clip left=0 top=675
	@wait time=1000
@jump target=*loop
