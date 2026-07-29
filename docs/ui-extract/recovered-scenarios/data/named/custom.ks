*
	; 選択肢配置領域の指定
	;[selopt left=0 top=60 width=800 height=360 shadow bold shadowColor=0 color=0xCBCACB overColor=0xFFFFFF]
	;normal="select_normal" over="select_over" entersebuf=8 clicksebuf=9
	;enterse='' clickse=''
	[selopt msgoff uistorage=select fadetime=200 left=0 top=90 width=&kag.scWidth height=600 size=39 color=0xFFFFFF edge edgeColor=0 edgeExtent=2 edgeEmphasis=1024]

	; ヒストリレイヤの uipsd
	[historyopt storage=backlog]

	; ゲーム中の右クリックメニューのデフォルト設定を変更
	; [sysrclickopt enabled=true call=true storage=sysmenu.ks target=""]

	; メッセージウィンドウの uipsd
	; メッセージウィンドウのオプション
;;	[meswinopt layer=message0 storage=text_window opacity=255 faceLeft=0 faceTop=0 faceWidth=150 faceHeight=150 nameLeft=181 nameTop=24 nameWidth=166 nameHeight=26 nameAlign=0 marginL=181 marginT=46 marginR=70 marginB=20 transparent=true visible=false]
	[meswinopt layer=message0 storage=window transparent=true nameAlign=-1 visible=false namevalign=0 nameabsolute=900 textabsolute=901]
;;	[meswinopt layer=message0 storage=window]

	; 辞書
	;;[encyclopedia color=0xFFC0C0]


	[addSysScript name="game" storage="start"]
	[addSysScript name="logo" storage="custom" target=*syslogo]
	[addSysScript name="extramode" storage="extra.ks"]
	[addSysScript name="extramode.from.exchview" storage="extra.ks" target=*start_from_exchview]

	[addSysScript name="title.from.logo"      storage="title.ks"  target=*start]
	[addSysScript name="title.from.game"      storage="custom.ks" target=*title]
	[addSysScript name="title.from.after"     storage="custom.ks" target=*title_after]
	[addSysScript name="title.from.title"     storage="custom.ks" target=*title_restore]
	[addSysScript name="title.from.load"      storage="custom.ks" target=*title_restore]
	[addSysScript name="title.from.option"    storage="custom.ks" target=*title_restore]
	[addSysScript name="title.from.cgmode"    storage="custom.ks" target=*title_restore_from_extra]
	[addSysScript name="title.from.scenemode" storage="custom.ks" target=*title_restore_from_extra]
	[addSysScript name="title.from.exchview"  storage="custom.ks" target=*title_restore_from_extra]
	[addSysScript name="title.from.voicemode" storage="custom.ks" target=*title_restore_from_extra]
	[addSysScript name="title.from.search"    storage="custom.ks" target=*title_review]
;;	[addSysScript name="scenemode.from.game"  storage="custom.ks" target=*extra_restore]
;;	[addSysScript name="scenemode.from.game"  storage="extra.ks"  target=*restore]
	[addSysHook   name="scenemode.view.init"     jump storage="custom.ks" target=*startrecollection]
;;	[addSysHook   name="scenemode.restore"       call storage="custom.ks" target=*endrecollection]
	[addSysHook   name="scenemode.start"         call storage="custom.ks" target=*title_bgm_scene]

	[addSysHook   name="first.logo"  call storage="custom.ks" target=*logo]
	[addSysHook   name="title.loop"  jump storage="custom.ks" target=*title]
	[addSysHook   name="title.game"  call storage="custom.ks" target=*title_game]

	[addSysHook   name="scnchart.jump.go"  call storage="custom.ks" target=*flowchart_go]

	[addSysHook   name="exchview.open.init" jump storage="custom.ks" target=*exchview_open]

	[addSysHook   name="exit.begin"        call storage="custom.ks" target=*end_hook]
	[addSysHook   name="exit.end"          call storage="custom.ks" target=*end_wait]
	[addSysHook   name="loadinit.start"    call storage="custom.ks" target=*trans_glitch]
	[addSysHook   name="titleback.start"    call storage="custom.ks" target=*trans_glitch]
	

	[addSysHook   name="cgmode.page.done"    call storage="custom.ks" target=*extra_clearstand]
	[addSysHook   name="scenemode.page.done" call storage="custom.ks" target=*extra_clearstand]
	[addSysHook   name="voicemode.page.done" call storage="custom.ks" target=*extra_clearstand]

	[addSysHook   name="search.back" jump storage="custom.ks" target=*search_back]

	[syscover visible color=0xFFFFFF]

	[return]


*caution
	;諸注意表示
	[stoptrans]
	[clearlayers]
	[ev file=attention notrans]
	[sysupdate]

	[syshook name="patch.check"]

	[clickskip enabled=true]

	[if exp="SystemConfig.XRated"]
	[sysvoice random]
	[endif]
	[sysvoice name=att0 chara=@]
	[beginskip]
	[syscover time=500 visible=false]
;;	[wait time=9000]
	[sysvoice wait]
	[wait time=300]
	[sysvoice name=att1 chara=@ wait]
	[wait time=1000]
	[sysvoice name=att2 chara=@ wait]
	[wait time=1000]
	[sysvoice name=att3 chara=@ wait]
	[wait time=1000]
	[endskip]

;	[stage 白画面 trans=normal time=500 sync]
[begintrans]
[ev hide]
[syslay file="width,1920,height,1080,color,0xFFFFFFFF" zorder=30]
[endtrans trans=normal time=500 sync]
	[return]

*logo
	@call target=*caution
*logo_show
	[startline]
	; ※効果音オブジェクトを強制生成(motionseで使用)
	[se stop]
	[sysvoice name=brand delayrun=1000]
	[delaystart nowarn]
	[ev storage=yuzulogo.mtn chara=LOGO motion=yuzulogo notrans]
;	[ev storage=yuzusourlogo.mtn chara=LOGO motion=yuzusourlogo notrans]
	[ev waitmovie]
	[allse stop]
	[delaycancel]

; 	add HIKARI FIELD & NekoNyan LOGO
	[ev file=hf_nn_logo]
	[wait time=2000]

	[ev storage=m2logo.mtn chara=m2cheeseware_logo motion=back_white notrans]
	[ev waitmovie]

	[begintrans]
	[all ontype=layer delete]
[syslay file="width,1920,height,1080,color,0xFFFFFFFF" notrans]
	[endtrans normal time=500 sync]
	@return

*syslogo
	[cancelskip]
	[cancelautomode]
	[clickskip enabled=false]
	[begintrans]
	[all ontype=layer delete]
	[msgoff]
;	[stage 白画面]
[syslay file="width,1920,height,1080,color,0xFFFFFFFF"]
	[endtrans trans=crossfade time=500 sync]
	[clickskip enabled=true]
	[call target=*logo_show]
	[sysjump from="logo" to="title"]

*title_bgm_scene
	@updatebgm storage=&tf.sceneModeLastBGM cond="tf.sceneModeLastBGM!=''"
	@eval exp="delete   tf.sceneModeLastBGM"
	@return

*title_bgm
	[updatebgm sflag storage=&SystemConfig.TitleBGM start=start cond="SystemConfig.TitleBGM!=''"]
	[return]

*title_common
	[linemode]
	;[XXX]Dramaticオフ暫定処理
	[eval exp="kag.dramaticModeWorking = false"]
	[store enabled=false storeonly]
	[quickmenu init]
	[stoptrans]
	[call target=*title_bgm cond=!tf.nobgmupdate]
	[eval exp="delete             tf.nobgmupdate"]
	[rclick enabled=false]
	[clickskip enabled=true]
	[dialog name="title"]
	[return]

*title_restore
	[backlay]
	[syspage free layer=message1 page=back]
	[systrans name=title.restore method=crossfade time=300]

	[call target=*title_common]
	[syspage current layer=message0 page=fore]
	[unlocklink]
	[jump target=*after_restore cond='kag.current.baseStorage=="afterstory__bg0"']
	;
	;{XXX} for multi language version hotfix
	[syspage uiload page=fore cond="Current.hasDefined('toggleLanguage')"]
	[jump target=*title_wait]

*title_reload
	[eval exp="tf.titleReload=true"]
*title_review
	[syshook name="title.review"]
	[call target=*title_common]
	[begintrans]
	[clearlayers page=back]
	[allimage hide delete]
	[if exp="!tf.titleReload || !GetTitleImageFile.UseMotion()"]
		[title_bg file='&GetTitleImageFile(true)' show]
		[title_logo show]
	[else]
;		[syslay_bg level=0 file=&GetTitleImageFile(true) show zoom=100:110 accel=-1 time=1500 nosync]
		[title_bg file='&GetTitleImageFile(false)' show]
	[endif]
	[syspage uiload page=back]
	[endtrans trans=sysclose time=300 sync]
	[eval exp="delete tf.titleReload"]
	[jump target=*title_wait]
*title_langchange
	[syspage uiload page=fore]
	[eval exp="world_object.refresh()"]
	[jump target=*title_wait]

*title
	[call target=*title_common]

	[begintrans]
	[allimage hide delete]
;	[白画面]
[syslay file="width,1920,height,1080,color,0xFFFFFFFF"]
	[endtrans notrans sync]

*title_start
	[cancelskip]
	[clickskip enabled=false]
	[if exp='!GetTitleImageFile.UseMotion()']
		[begintrans]
		[clearlayers page=back]
		[allimage hide delete]
		[title_bg file='&GetTitleImageFile(true)' show]
		[title_logo show]
		[systrans env name="title.show" method=crossfade time=500]
	[else]
		[clickskip enabled=true]
;		[syslay_bg level=0 file=&GetTitleImageFile(true) show zoom=100:110 accel=-1 time=1500 nosync]
		[title_bg file='&GetTitleImageFile(false)' show]
		[syslay delete]
		[title_bg waitmovie]
	[endif]
	[clickskip enabled=true]

	[syspage uiload page=fore visible=false]

	[sysvoice name=title]
	[msgon]

*title_wait
;;	[eval exp="CheckAllClearFlag()"]
	[eval exp="CustomExtraSetNextMode()"]
	[syspage current page=fore]
	; // [XXX] afterstoryを右クリックキャンセルできるようにするHack
	[rclick enabled jump storage=custom.ks target=*after_back cond='kag.current.baseStorage=="afterstory__bg0"']
	[jump storage=title.ks target=*wait]


*title_game
	[clickskip enabled=false]
	[fadeoutbgm time=1000]
	[begintrans]
	[allimage hide delete]
	[clearlayers page=back]
;	[endtrans fade=1000]
	[endtrans trans=sysfade time=1000]
	[return]


*continue
	[dialog action="onQLoad"]
	[locklink]
	[suspendload]
	[s]
	[gotostart]

*title_after
	[call target=*title_common]
	[cancelskip]
	[begintrans]
	[allimage hide delete]
	[clearlayers page=back]
	[endtrans notrans sync]
	[jump target=*after_show]
*after
	[locklink]
	[clickskip enabled=false]
;	[begintrans]
;	[allimage hide delete]
;	[clearlayers page=back]
;	[endtrans fade=500 sync]
*after_show
	[begintrans]
	[allimage hide delete]
	[clearlayers page=back]
	[syspage uiload storage=afterstory page=back]
	[endtrans trans=sysopen time=300 sync]
	[syspage current layer=message0 page=fore]
	[sysvoice name=after]
*after_restore
	[rclick enabled jump storage=custom.ks target=*after_back]
	[jump storage=title.ks target=*wait]

*after_back
	[locklink]
	[sysse name=cancel]
	[jump target=*title_review]


; ロード時トランジション
*trans_glitch
	[eval exp='tf.fadetrans="sysfade"']
	[return]

*end_hook
	; 「続きから」保存フック ⇒ onCloseHookからの呼び出しに変更
;;	[suspendsave]
	[sysvoice name=onexit]
	[donepanel]
	[quickmenu visible=false]
	[locklink]
	[return]
*end_wait
	[sysvoice wait]
	[return]

;----------------------------------------------------------------------
; [OBSOLETED] 古いコード
*to_quickload
	[history enabled=false]
	[dialog name=load load askload page=0]
	[syshook name="load.start"]
	[jump storage="load.ks" target="*open"] 
;;;					*page"]
*to_quickload_fromtitle
	[history enabled=false]
	[dialog name=load load askload page=0 fromtitle]
	[syshook name="load.start"]
	[jump storage="load.ks" target="*open"] 

*saveload_edit
	[rclick enabled=false]
	[panel class="SaveDataEdit"]
	[dialog action="onSaveDataEdit"]
	[s]
*jump_save_wait
	[rclick enabled jump storage="" target=*back_rclick]
	[jump storage="save.ks" target="*wait"]
*jump_load_wait
	[rclick enabled jump storage="" target=*back_rclick]
	[jump storage="load.ks" target="*wait"]
*jump_voice_wait
	[rclick enabled jump storage="" target=*back_rclick]
	[jump storage="voice.ks" target="*wait"]

;----------------------------------------------------------------------
; [NEW] for save/load link

*file_game_load
		[dialog done][jump storage=load.ks target=*start_save]
*file_title_load
		[dialog done][jump storage=load.ks target=*start_title]

*file_game_save
		[dialog done][jump storage=save.ks target=*start_load]
*file_title_save
		[dialog done][jump storage=save.ks target=*start_title]

*file_game_voicemode
		[dialog done][jump storage=voicemode.ks target=*start_load]
*file_title_voicemode
		[dialog done][jump storage=voicemode.ks target=*start_title]



;----------------------------------------------------------------------

*voicemode
	[sysjump from=title to=voicemode]
*extra
	[jump target=*voicemode cond=!.checkAnyClear]
	[jump storage=title.ks target=*extra]

*extra_failed
	[sysupdate]
	[gotostart]

*extra_clearstand
	[return     cond=!tf.clearStandImage]
	[eval exp="delete tf.clearStandImage"]
	[locklink]
	[allimage delete notrans sync]
	[unlocklink]
	[return]

*exchview
	[clearvar]
	[sysjump from="title" to="exchview"]
	[jump target=*extra_failed]

*exchview_open
	[locklink]
	[trans_stand state=setup]
	[init]
	;{NOTE} 背景オブジェクトを先行で生成しておかないと表示がおかしくなる
	[exchvbg hide]
	[dialog action="setup"]
	[sysupdate]

	[meswinload page=both]
	[syspage free page=back]
	[syspage uiload page=fore]
	[locklink]

	[dialog action="redraw" first updateall]
	[dialog action="updateButton"]
	[sysupdate]
	[trans_stand state=begin time=300]
	[wt]
	[trans_stand state=end]
	[stopaction]
;	[dialog action="refresh"]
	[unlocklink]
	[jump storage=exchview.ks target=*page_done]

*exchview_to_cgmode
	[sysjump from="exchview" to="cgmode"]
	[jump target=*extra_failed]

*exchview_to_scenemode
	[sysjump from="exchview" to="scenemode"]
	[jump target=*extra_failed]

*exchview_to_voicemode
	[sysjump from="exchview" to="voicemode"]
	[jump target=*extra_failed]

*voicemode
	[sysjump from="title" to="voicemode"]
	[jump target=*extra_failed]
*voiceload
	[call target=*before_replay]
	[eval exp='loadFunction("voiceload")']
	[s]
*voiceload_resume
*title_vload
	[sysse name="voice.back"]
	[bgm stop time=500]
	[begintrans]
	[clearlayers page=back]
	[envclearimage]
	[endtrans fade=300]
	[call storage=start.ks target=*reset]
	[eval exp="loadFunction('voicerestore')" cond=f.resumegame]
	[eval exp="tf.nobgmupdate=true"]
	[call target=*title_common]
	[call target=*title_bgm_scene]
	[begintrans]
	[clearlayers page=back]
	[allimage hide delete]
	[title_bg file='&GetTitleImageFile(true)' show]
	[syspage uiload page=back]
	[position layer=message1 page=back width=&kag.scWidth height=&kag.scHeight frame="" base="" color=0 opacity=255 visible=true]
	[endtrans fade=300 sync]
	[sysjump from="title" to="voicemode"]


*title_restore_from_extra
	[eval exp="delete tf.clearStandImage"]
	[syshook name="extra.reset"]
	[keepbgm]
	[jump target=*title_review]

*before_replay
	[clearvar]
	[call target=*before_replay_]
	[syshook name="extra.reset"]
	[return]
*before_replay_
	[rclick enabled=false jump=false]
	[locklink]
	[set name="tf.sceneModeLastBGM" value=&kag.bgm.playingStorage]
	[return]
*startrecollection
	[call target=*before_replay]
	[next storage="scenemode.ks" target=*view_start]

*extra_movie_start
	[call target=*before_replay_]
	[fadeoutbgm time=500]
	[syscover visible color=0x000000 time=500]
	[position layer=message0 page=fore visible=false]
	[position layer=message1 page=fore visible=false]
	[allimage delete sync]
	[syscover visible=false]
	[recollection storage=replay.ks target='&"*movie_"+tf.movie_play' donestorage=custom.ks donetarget=*extra_movie_done]
*extra_movie_done
	[call target=*title_bgm_scene]
	[dialog action=doneMovie]
	[jump storage=cgmode.ks target=*page]

*backlog_jump
	[locklink]
	[stoptrans]
	[backlay]
	[syspage  free page=back]
	[syshook  name="backlog.jump.init"]

	[dialog   action="onHide"]
	[systrans name="backlog.jump" method=crossfade time=300]
	[wt]
	[jump storage="backlog.ks" target=*jump_go]


*flowchart
	[sysjump from="title" to="scnchart"]
	[jump storage=title.ks target=*wait]
*flowchart_go
	[quickmenu fadein]
	[return]

*flowchart_from_backlog
	[dialog   action="onHide"]
	[sysjump from="game" to="scnchart"]
	[s]

*backlog_from_flowchart
	[sysjump from="game" to="backlog"]
	[s]


*search_back
	[stopvoice all]
	[locklink]
	[sysjump  from="search" to="title" back]
