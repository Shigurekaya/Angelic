;! clipleft=0 cliptop=0 clipwidth=1125 clipheight=675
	@loadcell storage="&checkAdult()?'sd003_adult':'sd003_cell'"
	@copy dx=649 dy=607 sx=0 sy=0 sw=98 sh=46
	@copy dx=649 dy=1282 sx=0 sy=0 sw=98 sh=46
*loop
; はね１
	@clip left=0 top=0
	@wait time=1000
; はね２
	@clip left=0 top=675
	@wait time=1000
@jump target=*loop
