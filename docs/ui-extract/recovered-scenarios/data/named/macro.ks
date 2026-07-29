;状態初期化用
;syscn から呼ばれるのでラインモード命令は含まない
[macro name=initbase]
[clearlayers]
[stopquake]
@stopbgm        cond=!mp.nostopbgm
@stopse buf=all cond=!mp.nostopse
[stopvideo]
[sysmovie state=end]
[history enabled=true]
[sysrclick]
[noeffect  enabled=true]
[clickskip enabled=true]
[current layer=message0]
[init nostopbgm=%nostopbgm]
[endmacro]

; ムービー再生のsflagはコンバートモード時のみ有効
; 非コンバートモードでは常にreloadを行う
[macro name=initmeswin][reloadmeswin *][endmacro]

; parsemacro.ks から呼ばれるポイント
*common_macro

;ラインモード指定とメッセージ初期化まで含む状態初期化用
[macro name=initscene]
[initbase *]
[initmode *]
[voeff clear cond=%translate|false]
[endmacro]

[macro name=initmode]
;[linemode mode=free craftername=true erafterpage=true]
[linemode mode=page erafterpage=true checknextvoice=true]
[autoindent mode=true]
[initmsgmode *]
[endmacro]

[macro name=initmsgmode]
[initmeswin * cond=%initmeswin|true]
; for rendermsgwin, multilang/translate
[msgmode mode=true history=true cond=%msgmode|false]
[msgmode mode=true history=true language=&GetScnConvertLangList() cond=%translate|false]
[endmacro]

; initmeswinから呼ばれる（※parsemacro経由の場合はは呼ばれないケースあり）
[macro name=reloadmeswin]
[meswinload page=both]
[endmacro]

;---------------------------------------------
; ムービー再生汎用
	;	file		再生するファイル
	;	mode		再生するモード
	;	cancelskip	再生前にスキップ停止
	;	skip		スキップ許可条件
	;	disablerclick	右クリックスキップ禁止
	;	beforetrans	事前トランジション
	;	beforecolor	事前フェードカラー
	;	aftercolor	事後カラー
	;	afterhide	事後消去トランジション
	[macro name=movie]
		[cancelskip cond=%cancelskip|false]
		[_movie_sysmenu_hide_]
		[beginskip skip=%skip eval='&mp.eval!=""?mp.eval:"sf.movie_"+(((string)mp.file).toLowerCase())']
			[begintrans]
				[msgoff]
				[allimage hide]
				[_movie_fill_ * coltag=beforecolor defcol=0x000000]
			[endtrans trans=%beforetrans|normal sync]
			[sysmovie file=%file disablerclick=%disablerclick mode=%mode begincolor=%beforecolor|0x000000 endcolor=%aftercolor|0x000000 keepcolor eval="kag.skipMode<SKIP_CANCEL" stopcheck="SKIP_CANCEL"]
			[begintrans]
				[clearlayers page=back]
				[_movie_fill_ *  coltag=aftercolor defcol=0x000000]
			[endtrans notrans sync]
			[sysmovie state=end]
			[if exp=%afterhide|true]
				[begintrans]
					[allimage hide]
					[layer name=_movie_fill_layer delete]
				[endtrans trans=%aftertrans|normal sync]
			[endif]
		[endskip]
		[_movie_sysmenu_restore_ *]
		[sflag name=&@"movie_${((string)mp.file).toLowerCase()}"]
	[endmacro]
	[macro name="_movie_fill_"]
		[layer name=_movie_fill_layer class=effect file='&@"color,${(mp[mp.coltag]!==void?+mp[mp.coltag]:+mp.defcol)&0xFFFFFF|0xFF000000},width,${kag.scWidth},height,${kag.scHeight}"']
	[endmacro]
	[macro name="_movie_sysmenu_hide_"]
;		[quickmenu fadeout]
	[endmacro]
	[macro name="_movie_sysmenu_restore_"]
;		[quickmenu fadein]
	[endmacro]

;// ------------------------------------------
;// 翻訳系

; 行頭の記号が解釈される問題を回避
[macro name=^*][ch text="*"][endmacro]
[macro name=^@][ch text="@"][endmacro]

; 行頭 * をエスケープ
[macro name="|*"][ch text="*"][endmacro]

; 英語シナリオ用全角フォント
[macro name=zenkaku][font face="スキップ"][ch text=%ch cond='mp.ch!=""'][emb exp=%emb cond='mp.emb!=""'][font face=user][endmacro]
[macro name=♪][zenkaku ch=♪][endmacro]
[macro name=…][zenkaku ch=…][endmacro]

; STEAM実績→data/steam/achievement.ini
[macro name=achievement][sflag prefix=ac_ name=%name][endmacro]

; R18場合分け
[macro name="checkadult"][next target=%target eval="checkAdult()"][endmacro]
[macro name="if-adult" ][if  exp="checkAdult()"][endmacro]
[macro name="if-allage"][if exp="!checkAdult()"][endmacro]

; チャット画面スタンプ・ステッカー（翻訳テキスト向け）
[macro name=stamp][font italic=true][graph storage='&GetPhoneChatStampImage(mp.icon,this)' alt="(Sticker)"][font italic=false][endmacro]

;---------------------------------------------

; 以下タイトルに必要なマクロを作成する

;// ------------------------------------------
;// 翻訳系

; 行頭の記号が解釈される問題を回避
[macro name=^*][ch text="*"][endmacro]
[macro name=^@][ch text="@"][endmacro]

; 行頭 * をエスケープ
[macro name="|*"][ch text="*"][endmacro]

; フォント固定

; STEAM実績→data/steam/achievement.ini
[macro name=achievement][sflag prefix=ac_ name=%name][endmacro]


;// ------------------------------------------
;// システム遷移系マクロ

[macro name="ゲーム終了：タイトル"    ][exit storage="start.ks" target="*gameend_title"][endmacro]
[macro name="ゲーム終了：ロゴ画面"    ][exit storage="start.ks" target="*gameend_logo" ][endmacro]
[macro name="ゲーム終了：アフター選択"][exit storage="start.ks" target="*gameend_after"][endmacro]

[macro name="シーン回想フラグ"][sflag name='&"replay_"+mp.flag'][endmacro]
[macro name="シーン回想終了"  ][シーン回想フラグ *][exit storage="replay.ks" target="*endrecollection" eval="kag.isRecollection"][endmacro]

; 
;[macro name="ゲーム開始"                                ][set name="tf.start_storage" value=%storage][set name="tf.start_target" value=%target|][exit storage="start.ks" target="*jump"][endmacro]
[macro name="ゲーム開始"][eval exp="delete tf.afterstory"][set name="tf.start_storage" value=%storage][set name="tf.start_target" value=%target|][exit storage="start.ks" target="*jump"][endmacro]
@if                            exp='typeof global.FilterScnChartXStorage=="Object"']
[macro name="シーン回想開始"][scenestart storage=&FilterScnChartXStorage(mp.storage) target=&GetSceneModeSubTarget(mp.target)][jump target=*envplay ignorewarn][endmacro]
@else
[macro name="シーン回想開始"][scenestart storage=%storage                            target=&GetSceneModeSubTarget(mp.target)][jump target=*envplay ignorewarn][endmacro]
@endif

; チャート画面用
[call storage=scnchart.ks target=*macro cond='Storages.isExistentStorage("scnchart.ks")']

; チャット画面用
[call storage=phonechat.ks target=*macro cond='Storages.isExistentStorage("phonechat.ks")']

; チャット発言効果音：左右で効果音を分ける
[macro name=chat_se]
	@if exp=%right|false
		@se file="♪LIENメッセージ２"
	@else
		@se file="♪LIENメッセージ１"
	@endif
[endmacro]

; チャット発言効果音：両方統一
;[macro name=chat_se][se file="♪LIEN通知２"][endmacro]

;// ------------------------------------------
;// テキスト・フォント系

[macro name=meswinchange][quickmenu fadeout][msgoff][_meswinchange *][quickmenu fadein][endmacro]

; ハートマーク描画
[macro name=_heart][font face=$ハート$ color=0xFFADD6][ch text=%text][resetfont][endmacro]
[macro name=▼][_heart text=&$9829][endmacro]
[macro name=▽][_heart text=&$9825][endmacro]
[macro name=&$9829][▼][endmacro]


; 倍率計算して指定する（基準サイズはdefaultFontSizeに合わせること）
;[macro name=xfont][font size='&mp.size>0?"x%f".sprintf(mp.size/26):mp.size'][endmacro]

;// ------------------------------------------

; 背景拡大用
[macro name=背景中]
[stage zoom=200 xpos=0 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景左]
[stage zoom=200 xpos=1200 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景右]
[stage zoom=200 xpos=-1200 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景左外]
[stage zoom=200 xpos=1500 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景右外]
[stage zoom=200 xpos=-1500 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景左大外]
[stage zoom=200 xpos=1800 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景右大外]
[stage zoom=200 xpos=-1800 ypos=-350]
[stage blur=2]
[endmacro]
[macro name=背景初期]
[stage zoom=100 xpos=0 ypos=0]
[stage blur=0]
[endmacro]
[macro name=背景拡大]
[stage zoom=150 xpos=0 ypos=-276]
[stage blur=1]
[endmacro]

[macro name=背景下]
[stage zoom=200 xpos=0 ypos=350]
[stage blur=2]
[endmacro]
[macro name=背景左下]
[stage zoom=200 xpos=900 ypos=350]
[stage blur=2]
[endmacro]
[macro name=背景右下]
[stage zoom=200 xpos=-900 ypos=350]
[stage blur=2]
[endmacro]

[macro name=アップ中]
[stage zoom=200 xpos=0 ypos=-350]
[endmacro]
[macro name=アップ左]
[stage zoom=200 xpos=1200 ypos=-350]
[endmacro]
[macro name=アップ右]
[stage zoom=200 xpos=-1200 ypos=-350]
[endmacro]
[macro name=アップ大外左]
[stage zoom=200 xpos=2000 ypos=-350]
[endmacro]
[macro name=アップ大外右]
[stage zoom=200 xpos=-2000 ypos=-350]
[endmacro]


;視点変化用1080
[macro name=視点変化]
;[layer name=ano_bar file=bar level=0 hide]
[begintrans]
;[chapter hide]
[bar_top show xpos=0 ypos=605]
[bar_und show xpos=0 ypos=-605]
[endtrans 0sec msgoff]
;[beginskip]
[bar_top xpos=0 ypos=495 time=750 nosync]
[bar_und xpos=0 ypos=-495 time=750 sync]
[bar_top stopaction]
;[endskip]
;[anotherview mode=1]
[meswinchange type=another]
[wait time=500]
[endmacro]

[macro name=視点通常]
[msgoff]
;[beginskip]
[bar_top ypos=605 time=750 nosync]
[bar_und ypos=-605 time=750 sync]
[bar_top stopaction]
;[endskip]
[begintrans]
[bar_top delete]
[bar_und delete]
[endtrans 0sec sync]
;[anotherview mode=0]
[meswinchange type=default]
;[chapter show]
[wait time=500]
[endmacro]

[macro name=視点変化ＣＧ]
[meswinchange type=another]
[endmacro]
[macro name=視点通常ＣＧ]
[meswinchange type=default]
[endmacro]

[macro name=黒半透明]
[msgoff]
[object name=half_trans class=centerlayer file=画面_黒 zoffset=40 hide 0sec]
[half_trans show 500sec opacity=100]
[endmacro]

[macro name=白半透明]
[msgoff]
[object name=half_trans class=centerlayer file=画面_白 zoffset=40 hide 0sec]
[half_trans show 500sec opacity=100]
[endmacro]

[macro name=透明解除]
[msgoff]
[half_trans hide 500sec]
[half_trans delete]
[endmacro]

; 集中線
[macro name=集中]
[concentration show]
[endmacro]

[macro name=集中解除]
[concentration delete]
[endmacro]

; 回想用
[macro name=妄想]
;[layer name=refrain 回想枠 level=6]
;[chapter hide]
[refrain show]
[endmacro]

[macro name=妄想解除]
;[layer name=refrain delete]
[refrain delete]
;[chapter show]
[endmacro]

; 覗き用
[macro name=覗き]
;[layer name=refrain 回想枠 level=6]
;[chapter hide]
[peeping show]
[endmacro]

[macro name=覗き解除]
;[layer name=refrain delete]
[peeping delete]
;[chapter show]
[endmacro]

[macro name=覗き横]
;[layer name=refrain 回想枠 level=6]
;[chapter hide]
[peeping_y show]
[endmacro]

[macro name=覗き横解除]
;[layer name=refrain delete]
[peeping_y delete]
;[chapter show]
[endmacro]


;// ------------------------------------------
;// アイキャッチ関連

[macro name=アイキャッチボイス]
[sysvoice eyecatch name=title chara=%chara]
[endmacro]

[macro name=共通アイキャッチ]
[quickmenu fadeout]
[msgoff]
[begintrans]
[object name=i_base class=centerlayer zoffset=100 file=アイキャッチ共通]
[i_base show]
[endtrans ターン]
[wait time=500]
[アイキャッチボイス chara="noa:ama:kur:kag:ori:fum"]
[wait time=2000]
[begintrans]
[i_base delete]
[暗転]
[endtrans ターン]
[quickmenu fadein]
[endmacro]

[macro name=アイキャッチ個別]
	[quickmenu fadeout]
	[msgoff]
	[eval exp='&@"tf.ec_random=intrandom(1,${mp.max})"']
	[begintrans]
		[ec_layer_base  zorder=200 order=0 file='&@"ec_${mp.tag}.pimg"' seton="base"]
		[ec_layer_open  zorder=200 order=1 file='&@"ec_${mp.tag}.pimg"' seton="open"]
		[ec_layer_chr0  zorder=200 order=2 file='&@"ec_${mp.tag}.pimg"' seton="0"]
		[ec_layer_chr1  zorder=200 order=3 file='&@"アイキャッチ${mp.name}rand"'      opacity=0]
		[ec_layer_close zorder=200 order=4 file='&@"ec_${mp.tag}.pimg"' seton="close" opacity=0]
		[ec_layer_logo  zorder=250 order=0 file="ec__logo_dot.pimg" seton="共通ロゴ" opacity=0]
		[ec_layer_dot   zorder=250 order=1 file="ec__logo_dot.pimg" seton="ドット"   opacity=0]
		[ec_motion file='&@"アイキャッチ${mp.name}show"']
	[endtrans ターン nosync]
	[beginskip]
	[wait time=800]
	[ec_motion file='&@"アイキャッチ${mp.name}show"']
	[wait time=700]
	[ec_layer_logo opacity=255 xpos=0:50 accel=-1 time=500 sync]
	[se file="♪アイキャッチ／カーテン"]
	[se file="☆コミカル29" fade=75]
	[begintrans]
		[ec_layer_chr0  delete]
		[ec_layer_open  hide]
		[ec_layer_close opacity=255]
	[endtrans 500sec sync]
	[wait time=500]
	[ec_motion file='&@"アイキャッチ${mp.name}open"' notrans]
	[se file="♪アイキャッチ／カーテン"]
	[se file="☆コミカル25" fade=50]
	[se file="☆キラキラ２"]
	[begintrans]
		[ec_layer_close  delete]
		[ec_layer_chr1   opacity=255]
		[ec_layer_open   show]
		[ec_layer_dot    opacity=255]
	[endtrans 300sec]
	[endskip]
	[アイキャッチボイス chara=%tag]
	[wait time=2000]
	[begintrans]
		[allfixcaption delete]
		[暗転]
	[endtrans ターン]
	[eval exp="delete tf.ec_random"]
	[quickmenu fadein]
[endmacro]

[macro name=アイキャッチ_乃愛  ][アイキャッチ個別 tag=noa max=6 name=乃愛  ][endmacro]
[macro name=アイキャッチ_天音  ][アイキャッチ個別 tag=ama max=6 name=天音  ][endmacro]
[macro name=アイキャッチ_来海  ][アイキャッチ個別 tag=kur max=6 name=来海  ][endmacro]
[macro name=アイキャッチ_かぐ耶][アイキャッチ個別 tag=kag max=6 name=かぐ耶][endmacro]
[macro name=アイキャッチ_オリエ][アイキャッチ個別 tag=ori max=4 name=オリエ][endmacro]
[macro name=アイキャッチ_風実花][アイキャッチ個別 tag=fum max=4 name=風実花][endmacro]


;//ＯＰを前作からひとまず流用してみる
[macro name=opmovie]
[beforemovie flag=movie_op]
[quickmenu fadeout wait]
[begintrans]
[all ontype=layer delete]
[endtrans 0sec msgoff]
[sysmovie file="OP" flag="movie_op" bgmflag=SongOP]
;BGMフラグを更新が必要？
;[白画面 notrans sync]
;[sysupdate]
[quickmenu visible=true hidden]
[sflag name="movie_op"]
;[暗転 1000sec sync]
[endmacro]

;//ＥＤも前作からひとまず流用してみる
;ボタン系を隠すコマンドを入れた方がいいかな、多分
[macro name=edmovie]
[lse  stop time=1000]
[lse2 stop time=1000]
[bgm  stop time=1000]
[quickmenu fadeout]
[msgoff]
[chapter hide]
[beforemovie flag=%flag]
[env sync]
;
[noeffect enabled=false]
[begintrans]
[allimage delete]
[endtrans normal time=1000 sync]
;[wait time=500 sync]
[sysmovie file=%file flag=%flag bgmflag=%bgm]
[noeffect enabled=true]
[env sync]
[quickmenu visible=true hidden]
[sflag name=%flag cond='mp.flag!=""']
[endmacro]


;[macro name=songmovie]
;[cancelskip]
;[quickmenu fadeout wait]
;[begintrans]
;[all ontype=layer delete]
;[endtrans 0sec msgoff]
;[sysmovie file="wakanasong" flag="movie_song" bgmflag=BGM52 begincolor=0x000000 endcolor=0xFFFFFF]
;;BGMフラグを更新しないといけないですね
;[白画面 notrans sync]
;;[sysupdate]
;[quickmenu fadein]
;;[暗転 1000sec sync]
;[endmacro]


[macro name=scenewear_seladd][emb escape=false exp=_scenewear_seladd_emb(mp)][endmacro]
[macro name=メガネ選択]
[initscene]
	[scenewear_seladd flag=true  text="眼鏡もかけていただけると……"	tag="MM_01A" exp='SetBranchFlags("s410*part_410_sel1",1)']
	[scenewear_seladd flag=false text="なんでもないです"			tag="MM_01B" exp='SetBranchFlags("s410*part_410_sel1",2)']
[select][msgoff][ws buf=9]
[endmacro]

@return
