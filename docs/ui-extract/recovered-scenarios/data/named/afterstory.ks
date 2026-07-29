;
; シーンモード
;

*start
	[syshook name="afterstory.start"]
	[syshook name="afterstory.start.fromtitle"]
	[rclick enabled=false jump=false]
	[dialog name=afterstory fromTitle]
	[jump target=*open]

; ゲームから復帰する
*fromgame
	[syshook name="afterstory.start"]
	[syshook name="afterstory.start.restore"]
	[rclick enabled=false jump=false]
	[dialog name=afterstory fromGame]
	[jump target=*open]

*open
	[stoptrans]
	[backlay cond=Current.propget('fromTitle')]

	[syshook name="afterstory.open.init"]
	[syspage uiload page=back]

	[systrans name="afterstory.open" method=crossfade time=300]
	[wt]
	[jump target=*page_done]

*page
	[stoptrans]
	[backlay cond=Current.propget('fromTitle')]

	[syshook name="afterstory.page.init"]
	[syspage uiload page=back]

	[systrans name="afterstory.page" method=crossfade time=300]
	[wt]
*page_done
	[syspage current page=fore]
	[rclick enabled jump storage="" target=*back_rclick]

	[syshook name="afterstory.page.done"]
*wait
	[s]
	[s]

*view
	[rclick enabled=false jump=false]
	[locklink]
	[syshook name="afterstory.view"]
	[historyopt uiload]
	[sysinit]
	[eval exp='tf.recollect=Current.action("view")']
	[s]

*back_rclick
	; 右クリック効果音
	[sysse name="afterstory.rclick"]
*back
	[syshook name="afterstory.back"]
	[sysjump from="afterstory" to="title" back]

*cgmode
	[sysjump from="afterstory" to="cgmode"]

*scenemode
	[sysjump from="afterstory" to="scenemode"]

*soundmode
	[sysjump from="afterstory" to="soundmode"]

