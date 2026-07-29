;; シーン鑑賞用

; シーンプレイ処理
*envplay|
		[current layer=message0 page=fore]
		[initmode msgmode initmeswin=false]
		[linemode]
		[syscurrent name="game"]
		[sceneplay]
		[exit storage="replay.ks" target="*endrecollection"]
		[s]

; 終了時演出
*endrecollection|
		[call storage=start.ks			target=*reset]
		[waitrclickup]
		[endrecollection]

*voice_jump|
		[meswinload page=both]
		[quickmenu fadein]
		[jump			target=*envplay ignorewarn]

*search_jump|
		[meswinload page=both]
		[quickmenu fadein]
		[dialog  action=invokeJump]
		[s]

; ムービー類

*movie_op|
		[opmovie][waitrclickup][endrecollection]

*movie_ed_noa|
		[sysmovie file=ed1_noa][waitrclickup][endrecollection]
*movie_ed_ama|
		[sysmovie file=ed2_amane][waitrclickup][endrecollection]
*movie_ed_kur|
		[sysmovie file=ed3_kurumi][waitrclickup][endrecollection]
*movie_ed_kag|
		[sysmovie file=ed4_kaguya][waitrclickup][endrecollection]
*movie_ed_ori|
		[sysmovie file=ed5_orie][waitrclickup][endrecollection]
*movie_ed_fum|
		[sysmovie file=ed6_fumika][waitrclickup][endrecollection]

