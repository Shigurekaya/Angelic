*dummy|

[initscene]
シーン回想テスト用ダミーです。

[endrecollection]

;---------------------------------------------------------------
*chara1_typeA_jump|

[initscene]

終了ラベル名を通過すると自動で終了します。

*chara1_typeA_end|
*|

↑必ず直後に「*|」の無名ラベルを記入してください。

;---------------------------------------------------------------
*chara1_typeB_jump|

[initscene]

ここは非表示スキップされます。

*chara1_typeB_skip|

ここから開始されます。

終了ラベル指定なしの場合はendrecollectionタグで終了します

[endrecollection]

ここは再生されません。

[gotostart]
