; コンバートモードではKAG用の初期化は不要
[macro name=initbase]
[init nostopbgm=%nostopbgm]
[endmacro]

;// [XXX] モジュール依存問題
[if exp='typeof global.MessageFrameChanger=="Object"']
	; onEnvInitで初期化されることを想定
	[macro name=initmeswin][endmacro]
[else]
	[macro name=initmeswin][reloadmeswin *][endmacro]
[endif]

[if exp="typeof global.createCallConfigFile == 'undefined'"]
	; 旧方式
	[call storage=macro.ks target=*common_macro]
[else]
	; 新方式（append側のmacro.ks対応／システム系マクロ対応）
	[emb escape=false exp="createCallConfigFile('macro.ks', '*common_macro')"]
	[emb escape=false exp="SystemConfig.systemMacroTexts.join('')" cond="SystemConfig.systemMacroTexts instanceof 'Array'"]
[endif]
