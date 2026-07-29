; 
; シナリオ選択画面
;

*start_title
	[clearvar]
	[delaycancel]
	[dialog  name="scnchart" fromTitle]
	[syshook name="scnchart.start"]
	[jump target=*open]

*start_title_from_subscn
	[syshook name="scnchart.reset"]
	[sysjump from=title to=scnchart]

*start_game
	[history enabled=false]
	[dialog  name="scnchart"]
	[syshook name="scnchart.start"]

*open
	[stoptrans]
	[backlay]

	[syshook name="scnchart.open.init"]
	[syspage uiload page=back]

	[systrans name="scnchart.open" method=crossfade time=300]
	[wt]
	[jump target=*page_done]

*page
	[stoptrans]
	[backlay]

	[syshook name="scnchart.page.init"]
	[syspage uiload page=back]

	[systrans name="scnchart.page" method=crossfade time=300]
	[wt]
*page_done
	[syspage current page=fore]
	[rclick enabled jump storage="scnchart.ks" target=*back]

	[syshook name="scnchart.page.done"]
*wait
	[s]

*back
;;	[sysse name="scnchart.close"]
	[jump target=*to_title cond=&'Current.propget("fromTitle")']

; ゲームに戻る
*to_game
	[sysjump from="scnchart" to="game" back]

; タイトルに戻る
*to_title
	[sysjump from="scnchart" to="title" back]


; 復帰処理
*return
	[backlay]
	[syspage free page=back]
	[stoptrans]
	[syshook  name="scnchart.close.init"]
	[systrans name="scnchart.close" method=crossfade time=300]
	[wt]

	[syshook name="scnchart.close.done"]
	[sysrestore_backtogame]
	[return]

*jump_from_extra
	[return storage=scnchart.ks target=*jump]
*jump
	[locklink]
	[delaycancel]
	[bgm stop=500]
	[allse stop=500]
	[envstop time=500]
	[fadeoutbgm time=500]
	[fadeoutse buf=all time=500]
	[dialog done]
	;
	[begintrans]
	[syshook name="scnchart.jump.init"]
	[syspage free page=back]
	[syspage free layer=message0 page=back]
	[clearlayers page=back]
	[envclear]
	[all ontype=layer delete]
	[endtrans fade=500 sync]
	[syshook name="scnchart.jump.done"]
*jump_go
	[store enabled=true]
	[sysrestore]
;	[clearlayers page=fore]
;	[backlay]
	[historyopt uiload]
	[sysinit]
	[stopse buf=all]
	[syscurrent name="game" cond=!world_object.playerExecMode]
	[syshook name="scnchart.jump.go"]
	[initscene]
	[init sync]
	[sysupdate]
	;
	@scnchart reset
	@eval exp="doLoadFadeIn()"
	@jump storage="start.ks" target=*jump ignorewarn
	[s]
	[s]

*select
	[rclick enabled jump storage="scnchart.ks" target=*hideselect]
	[locklink]
	[s]
*hideselect
	[dialog action="hideSelect"]
*waitselect
	[rclick enabled=false]
	[s]
*doneselect
	[dialog action="doneSelect"]
	[rclick enabled jump storage="scnchart.ks" target=*back]
	[unlocklink]
	[jump target=*wait]

*sysfrom_title
	[sysjump from="title" to="scnchart"]
*sysfrom_game
	[sysjump from="game"  to="scnchart"]

	[s]
	[s]

*macro
	[eval exp="dm('* scnchart:macro enabled')" cond=debugWindowEnabled]
	; for auto scene macro
	[macro name="beginscene"                    ][emb escape=false exp="MakeScnChartMacro(this,mp,true)" ][endmacro]
	[macro name="endscene"   ][sflag name=_break][emb escape=false exp="MakeScnChartMacro(this,mp,false)"][endmacro]
	[macro name="selectscene"][beginscene checktype="select"][endmacro]
	[macro name="branchscene"][beginscene checktype="branch"][endmacro]
	; for _chartmacro.ks
	@macro name="chartmap"
		@set name="f.currentChartPos" value="&mp.leave?'':mp.enter"
		@scnchart *
	@endmacro
	[if exp='typeof global.MakeScnChartXNext=="Object"']
		; [XXX] R18 filename hack
		[macro name=x_next][emb escape=false exp="MakeScnChartXNext(this,mp)"][endmacro]
	[else]
		[macro name=x_next][next *][endmacro]
	[endif]
	@call storage="&SystemConfig.scnchartMacroFile" cond="SystemConfig.scnchartMacroFile != '' && Storages.isExistentStorage(SystemConfig.scnchartMacroFile)"
	[return]
