;
; 検索画面
;

*start_title
	[linemode]
	[dialog   name="search"]
	[syshook  name="search.start"]
	[sysse    name="search.open"]
*open
	[stoptrans]
	[backlay]

	[syshook  name="search.open.init"]
	[syspage current page=back]
	[syspage  uiload page=back]

	[dialog   action="onShow"]
	[systrans name="search.open" method=crossfade time=300]
	[wt]
	[jump target=*page_done]

*start_voice
	[linemode]
	[dialog   name="search" research]
	[syshook  name="search.start"]
	[jump target=*page]

*start_game
	[linemode]
	[cancelskip]
	[cancelautomode]
	[history enabled=false]
	;
	; // XXX
	[xchgbgm storage=&SystemConfig.TitleBGM time=1000]
	;
	[stopvoice all]
	[bgm  stop time=1000]
	[all ontype=sound stop=1000]
	;
	[begintrans]
	[msgoff]
	[envclear]
	[allimage hide delete]
;	[ev file="search_bg"]
	[ev file="title_bg"]
	[endtrans fade=300 sync]
	;
	[dialog   name="search" research]
	[syshook  name="search.start"]
	[sysse    name="search.open"]

*page
	[stoptrans]
	[clearlayers page=back]

	[syshook  name="search.page.init"]
	[syspage current page=back]
	[syspage  uiload page=back]

	[dialog   action="onShow"]
	[systrans name="search.page" method=crossfade time=300]
	[wt]

*page_done
	[stoptrans]
	[syspage  current page=fore]
	[rclick   enabled jump storage="" target=*back_rclick]

	[syshook  name="search.page.done"]
*wait
	[s]
	[s]

*jump
	[fadeoutbgm time=1000]
	[stoptrans]
	[backlay]
	[syspage  free page=back]
	[syshook  name="search.jump.init"]

	[dialog   action="onHide"]

	[dialog   action="onHide"]
	[systrans name="search.jump" method=crossfade time=300]
	[wt]

	[clearvar]
	[historyopt uiload]
;;;	[sysinit]
;;;	[initscene]
	[quickmenu fadein]

	[syscurrent name="game"]
	[sysrestore]

	[syshook  name="search.jump"]
;;	[dialog  action=invokeJump]
	[recollection storage="replay.ks" target="*search_jump" doneStorage="search.ks" doneTarget="*sysfrom_game"]
	[s]

*back_rclick
	[syshook  name="search.rclick"]
*back
	[sysse    name="search.close"]
	[syshook  name="search.back"]

; ゲームに戻る
*game
	[stopvoice all]
	[locklink]
	[stoptrans]
	[backlay]
	[syspage  free page=back]
	[syshook  name="search.close.init"]

	[dialog   action="onHide"]
	[systrans name="search.close" method=crossfade time=300]
	[wt]

	[syshook  name="search.close.done"]
	[sysjump  from="search" to="title" back]

*sysfrom_title
	[sysjump from="title" to="search"]

*sysfrom_game
	[sysjump  from="game" to="search"]

