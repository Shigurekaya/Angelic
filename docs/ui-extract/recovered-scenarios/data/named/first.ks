[linemode]

@loadplugin module=extrans.dll   cond=KAGConfigEnabled("extransEnabled",true)
@loadplugin module=extNagano.dll cond=KAGConfigEnabled("extNaganoEnabled")

@if exp="!SystemConfig.referAppendVersion"
	@call storage="version.ks"
@else
	[emb escape=false exp="createCallConfigFile('version.ks')"]
@endif
@nowait
@textwrite enabled=false
@beginskip skip=true
@if    exp="typeof tf.__origDebugLevel == 'undefined' && System.getArgument('-debug') != 'yes'"
	; マクロ読み込み時はデバッグログを無効に（長いと起動が遅くなるので）
	@eval exp="tf.__origDebugLevel = tkdlNone, tf.__origDebugLevel <-> kag.debugLevel" 
	@call target=*macro
	@eval exp="tf.__origDebugLevel <-> kag.debugLevel"
@else
	@call target=*macro
@endif
@endskip
@cancelskip
;@call storage="custom.ks"
[emb escape=false exp="createCallConfigFile('custom.ks')"]
@endnowait
@textwrite enabled=true
;
; wait for full-screen changed
@waitstable
;
*first
[syshook name="first.init"]
[syshook name="first.logo" cond=!SystemConfig.stopSkipOnMessageReceived]
[sysjump from="first" to="title"]
[s]

*reset
[clearallmacro]
@call target=*macro
[jump target=*first]

;---------------------------------------------------------------
*macro
[syshook name="macro.init"]
; script macros
;[call storage="macro.ks"]
[emb escape=false exp="createCallConfigFile('macro.ks')"]
; system macros
@macro name=sysrestore_backtogame
	@if exp="kag.getKeyState(VK_RBUTTON) && (kag.selectShowing || kag.mapSelectShowing || kag.panelShowing)"
		[rclick enabled=false][syscover clear visible][waitrclickup][syscover visible=false]
	@endif
	@sysrestore
@endmacro
[emb escape=false exp="SystemConfig.systemMacroTexts.join('')" cond="SystemConfig.systemMacroTexts instanceof 'Array'"]
[syshook name="macro.done"]
@return
