*loadinit
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="loadinit",  tf.noclearhistory=false']
*gobacktitle
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="titleback", tf.noclearhistory=false']
*endrecollection
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="endreplay", tf.noclearhistory=false']
*afterstory
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="afterstart",tf.noclearhistory=false']
*emergencyreboot
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="emerinit",  tf.noclearhistory=false']
*noclearhistory
		[exit noautolabel storage=loadinit.ks target=*doload exp='tf.loadinit="previnit",  tf.noclearhistory=true']
;
*exec
[syscurrent name="game"]
[historyopt uiload]
[freesnapshot]
[initbase]
[sysupdate]
[return]
;
*convert
[linemode]
[initbase]
[waittrig name=convert]
[gotostart]
;
*doload
[linemode]
; ロード処理
[clickskip enabled=false]
[video visible=false]
[locklink]
;
[eval exp='tf.fadetime=1000,tf.fadetrans=void']
[syshook name=&'tf.loadinit+".start"']
;
; 画面・BGMフェードアウト
[fadeoutbgm time=&tf.fadetime cond="tf.fadetime>0"]
[envstop    time=&tf.fadetime cond="tf.fadetime>0"]
;[bgm stop  time=&tf.fadetime cond="tf.fadetime>0"]
[delaycancel]
[stoptrans]
[eval exp=terminator.invoke()]
[begintrans]
[clearlayers page=back]
[envclearimage]
;[allimage hide]
;[all ontype=layer delete]
;[systrans env name=&tf.loadinit method=crossfade time=&tf.fadetime]
;[wt]
[endtrans trans='&tf.fadetrans!=""?tf.fadetrans:"crossfade"' time=&tf.fadetime sync]
;
[syshook name=&'tf.loadinit+".end"']
[syscurrent name="game"]
[historyopt uiload]
[clearhistory cond="!tf.noclearhistory"]
[initbase nostopse=&tf.loadinitnostopse]
[eval exp="doLoad()"]
[sysupdate]
*exit
