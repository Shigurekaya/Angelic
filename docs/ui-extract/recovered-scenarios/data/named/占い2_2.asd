	@loadcell storage="占い__cell"
*loop
; しっぽ
	@copy dx=22 dy=555 sx=0 sy=0 sw=300 sh=300
	@wait time=1000
; しっぽ２
	@copy dx=22 dy=555 sx=300 sy=0 sw=300 sh=300
	@wait time=1000
@jump target=*loop
