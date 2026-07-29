;
; 立ち絵鑑賞モード
;

*start
	[syshook name="exchview.start"]
	[rclick enabled=false jump=false]
	[history output=false enabled=false]
	[dialog name=exchview]

*open
	[syshook name="exchview.open.init"]

*open_new
	[locklink]
	[dialog action="trans_setup"]
	[init]
	[dialog action="setup"]
;	[sysupdate]

	[syshook name="exchview.open.setup"]
	[meswinload page=both]
*open_trans
	[syspage free page=back]
	[syspage uiload page=fore]
	; {NOTE} uiloadでロックが解除されてしまうので再度ロック
	[locklink]

	[syspage current page=fore]
	[dialog action="redraw" first updatediff]
	[dialog action="updateButton"]
	; {NOTE} キャプチャ猶予
	[sysupdate]
	[dialog retval action="trans_begin" trans="exchview.open" method=crossfade time=300]
	[wt]
	[dialog action="trans_end"]
	[stopaction]
	[unlocklink]
	[jump target=*page_done]

*open_old
	[begintrans]

	[dialog action="setup" parserun]

	[clearlayers page=back]
	[syspage uiload  page=back]
	[syspage current page=back]

	[dialog action="redraw" parserun first]
	[dialog action="updateButton"]

	[syshook name="exchview.open"]
	[systrans env name="exchview.open" method=crossfade time=300]
	[wt]
	[jump target=*page_done]

*page
	[begintrans]
	[if exp=SystemConfig.ExChViewUseOldRedrawMethod][all ontype=layer hide][all ontype=dlayer hide][endif]
	;[clearlayers page=back]

	[syshook name="exchview.page.init"]
	[syspage uiload  page=back]
	[syspage current page=back]

	[dialog action="redraw" parserun]
	[dialog action="updateButton"]

	[syshook name="exchview.page"]
	[systrans env name="exchview.page" method=crossfade time=300]
	[wt]

*page_done
	[syspage current page=fore]
	[dialog action="updateDragMask"]

	[rclick enabled jump storage="" target=*rclick]

	[syshook name="exchview.page.done"]
*wait
	[syshook name="exchview.wait"]
	[s]
	[s]

*update
	[dialog action="beforeUpdate"]

	[jump target=*update_old cond=SystemConfig.ExChViewUseOldRedrawMethod]
	[dialog action="redraw" parserun updatediff]
	[jump target=*update_ui]
*update_old
	[locklink]
	[begintrans]
	[all ontype=layer hide][all ontype=dlayer hide]

	[dialog action="redraw" parserun]

	[endtrans notrans sync]

	[syspage current page=fore]
*update_ui
	[unlocklink]

	[dialog action="updateButton"]
	[dialog action="updateDragMask"]

	[sysupdate]
	[jump target=*wait]

*view
	[locklink]
	[syshook name="exchview.view.init"]
	[jump target=*view_done cond=!kag.current.visible]

	[rclick enabled jump storage="" target=*view]
	[dialog action=onViewStart parserun]
	[syshook name="exchview.view.wait"]
	[dialog action=onViewWait]
	[s]

*view_wait
	[waitclick]
	[sysse name="exchview.view.click"]
	[jump target=*view_end]

*view_done
	[sysse name="exchview.view.done"]
*view_end
	[dialog action=onViewEnd parserun]
*capture_end
	[unlocklink]
	[rclick enabled jump storage="" target=*rclick]
	[dialog action="updateDragMask"]
	[jump target=*wait]

*capture
	[dialog action=onViewStart parserun capture]
	[envupdate]
	[sysupdate]
	[dialog action=captureScreen]
	[wait time=100]
	[dialog action=onViewEnd   parserun capture]
	[jump target=*capture_end]

*changestage
	[jump target=*nopanel cond='!Current.cmd("canStageSelect")']
	[sysse name="ok"]
	[exchview_panel name="stageselect"]
	[s]
*changetime
	[jump target=*nopanel cond='!Current.cmd("canTimeSelect")']
	[sysse name="ok"]
	[exchview_panel name="timeselect"]
	[s]
*changeface
	[jump target=*nopanel cond='!Current.cmd("canFaceSelect")']
	[sysse name="ok"]
	[exchview_panel name="faceselect"]
	[s]
*panelupdate
	[jump target=*panelupdate_old cond=SystemConfig.ExChViewUseOldRedrawMethod]
	[dialog action="redraw" parserun updatediff]
	[s]
*panelupdate_old
	[begintrans]
	[all ontype=layer hide][all ontype=dlayer hide][endif]
	[dialog action="redraw" parserun]
	[endtrans notrans sync]
	[s]

*panelclose
	[donepanel]
*nopanel
	[sysse name="cancel"]
	[jump target=*update]


*rclick
	[jump target='&Current.cmd("getRclickJumpTarget")']

*back_rclick
	; 右クリック効果音
	[sysse name="exchview.rclick"]
*back
	[syshook name="exchview.back"]
	[sysjump from="exchview" to="title" back]
*back2
	[syshook name="exchview.back"]
	[sysjump from="exchview" to="title"]

*askquit
	[locklink]
	[waitrclickup]
	[dialog action=askQuit]
	[s]
	[s]


*cgmode
	[syshook name="exchview.jump.cgmode"]
	[sysjump from="exchview" to="cgmode"]

*scenemode
	[syshook name="exchview.jump.scenemode"]
	[sysjump from="exchview" to="scenemode"]

*soundmode
	[syshook name="exchview.jump.soundmode"]
	[sysjump from="exchview" to="soundmode"]

