*start|
[initscene]
[quickmenu fadein notify]

; 既読自動ジャンプの確認
;[check_readjump route=&tf.afterstory]

@syshook name="start.afterstory" cond='tf.afterstory!=""'

;開始シナリオを下記に記入
[ゲーム開始 storage="【共通】01.ks"]

;---------------------------------------------------------------------
; 起動処理用スクリプト。コンバートモードかどうかで挙動を変更
*jump|
[eval exp="tf.start_storage = FilterScnChartXStorage(tf.start_storage)" cond="typeof global.FilterScnChartXStorage == 'Object'"]
[jump target=*envstart cond=world_object.playerExecMode ignorewarn]
[next storage=&tf.start_storage target=&tf.start_target exp="delete tf.start_storage, delete tf.start_target, delete tf.start_point"]

*envstart|
	[syscurrent name="start"]
	[initscene msgmode]
	[linemode]
	[scenestart storage=&tf.start_storage target=&tf.start_target point=&tf.start_point]
	[eval    exp="delete tf.start_storage, delete tf.start_target,delete tf.start_point"]
	[syscurrent name="game"]
*envplay|
	[sceneplay]
	[exit storage="start.ks" target="*gameend_title"]
	[s]

*gameend_after
	[call target=*reset]
	[sysjump from="after" to="title"]
	[gotostart]
	[s]

*gameend_title
	[call target=*reset]
	[sysjump from="game" to="title"]
	[gotostart]
	[s]

*gameend_logo
	[call target=*reset]
	[sysjump from="game" to="logo"]
	[gotostart]
	[s]

*reset
	[cancelskip]
	[cancelautomode]
	[endrecollection]
	[envclear]
	[initbase]
	[linemode]
	[return]

