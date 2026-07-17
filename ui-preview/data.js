window.UI_DATA = {
  "game": "天使☆嚣嚣 RE-BOOT!",
  "engine": "Angelic",
  "layout": "angelic-bottom-menu+pixel-settings",
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "title": {
    "style": "bottom-bar",
    "bg": "assets/title/bg0.png",
    "logo": "assets/title/logo_cn.png",
    "logo_pos": {
      "x": 36,
      "y": 36,
      "w": 640
    },
    "backgrounds": [
      {
        "index": 0,
        "src": "assets/title/bg0.png",
        "label": "背景1"
      },
      {
        "index": 1,
        "src": "assets/title/bg1.png",
        "label": "背景2"
      },
      {
        "index": 2,
        "src": "assets/title/bg2.png",
        "label": "背景3"
      },
      {
        "index": 3,
        "src": "assets/title/bg3.png",
        "label": "背景4"
      },
      {
        "index": 4,
        "src": "assets/title/bg4.png",
        "label": "背景5"
      },
      {
        "index": 5,
        "src": "assets/title/bg5.png",
        "label": "背景6"
      },
      {
        "index": 6,
        "src": "assets/title/bg6.png",
        "label": "背景7"
      },
      {
        "index": 7,
        "src": "assets/title/bg7.png",
        "label": "背景8"
      }
    ],
    "buttons": [
      {
        "id": "start",
        "label": "从头开始",
        "action": "start"
      },
      {
        "id": "continue",
        "label": "继续游戏",
        "action": "start"
      },
      {
        "id": "load",
        "label": "载入进度",
        "action": "load"
      },
      {
        "id": "flowchart",
        "label": "流程图",
        "action": "flowchart"
      },
      {
        "id": "extra",
        "label": "鉴赏模式",
        "action": "cg"
      },
      {
        "id": "after",
        "label": "附加剧情",
        "action": "toast"
      },
      {
        "id": "option",
        "label": "游戏设置",
        "action": "settings"
      },
      {
        "id": "exit",
        "label": "退出游戏",
        "action": "toast"
      }
    ],
    "sources": [
      "title.ks",
      "uipsd/title.pbd",
      "image/title_bg*.png",
      "locale/cn/title_logo_cn.png"
    ]
  },
  "settings": {
    "style": "pixel-stack",
    "bg": "assets/settings/bg.png",
    "chassis": "assets/settings/option__pack.png",
    "tabs": [
      {
        "id": "0",
        "label": "基本设置",
        "mode": "pixel",
        "hotspots": [
          {
            "key": "fullscreen",
            "label": "画面尺寸",
            "type": "toggle",
            "options": [
              "窗口",
              "全屏"
            ],
            "col": 0,
            "row": 0,
            "x": 129,
            "y": 148,
            "w": 822,
            "h": 150
          },
          {
            "key": "sqscr",
            "label": "画面比例",
            "type": "toggle",
            "options": [
              "16:9",
              "4:3"
            ],
            "col": 0,
            "row": 1,
            "x": 129,
            "y": 306,
            "w": 822,
            "h": 150
          },
          {
            "key": "textspeed",
            "label": "文本速度",
            "type": "slider",
            "col": 0,
            "row": 2,
            "x": 129,
            "y": 464,
            "w": 822,
            "h": 150
          },
          {
            "key": "autospeed",
            "label": "自动速度",
            "type": "slider",
            "col": 0,
            "row": 3,
            "x": 129,
            "y": 622,
            "w": 822,
            "h": 150
          },
          {
            "key": "skipall",
            "label": "未读跳过",
            "type": "toggle",
            "options": [
              "仅已读",
              "全部"
            ],
            "col": 0,
            "row": 4,
            "x": 129,
            "y": 780,
            "w": 822,
            "h": 150
          },
          {
            "key": "wave",
            "label": "主音量",
            "type": "slider",
            "col": 1,
            "row": 0,
            "x": 967,
            "y": 148,
            "w": 822,
            "h": 150
          },
          {
            "key": "bgm",
            "label": "BGM",
            "type": "slider",
            "col": 1,
            "row": 1,
            "x": 967,
            "y": 306,
            "w": 822,
            "h": 150
          },
          {
            "key": "se",
            "label": "音效",
            "type": "slider",
            "col": 1,
            "row": 2,
            "x": 967,
            "y": 464,
            "w": 822,
            "h": 150
          },
          {
            "key": "voice",
            "label": "语音",
            "type": "slider",
            "col": 1,
            "row": 3,
            "x": 967,
            "y": 622,
            "w": 822,
            "h": 150
          },
          {
            "key": "movie",
            "label": "影片",
            "type": "slider",
            "col": 1,
            "row": 4,
            "x": 967,
            "y": 780,
            "w": 822,
            "h": 150
          }
        ],
        "pack": null
      },
      {
        "id": "1",
        "label": "画面设置",
        "mode": "panel",
        "rows": [
          {
            "key": "0_panictype",
            "label": "0_panictype",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/panictype/0"
            ]
          },
          {
            "key": "1_panictype",
            "label": "1_panictype",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/panictype/1"
            ]
          },
          {
            "key": "2_panictype",
            "label": "2_panictype",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/panictype/2"
            ]
          },
          {
            "key": "3_panictype",
            "label": "3_panictype",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/panictype/3"
            ]
          },
          {
            "key": "changeBasicSlider",
            "label": "changeBasicSlider",
            "type": "button",
            "bindings": [
              "changeBasicSlider",
              "changeBasicSlider"
            ]
          },
          {
            "key": "changeSysArg",
            "label": "changeSysArg",
            "type": "toggle",
            "bindings": [
              "changeSysArg/toggle/curmove",
              "changeSysArg/false/curmove",
              "changeSysArg/true/curmove",
              "changeSysArg/toggle/curmove",
              "changeSysArg/toggle/scanim",
              "changeSysArg/false/scanim",
              "changeSysArg/true/scanim",
              "changeSysArg/toggle/scanim",
              "changeSysArg/toggle/sqscr",
              "changeSysArg/false/sqscr",
              "changeSysArg/true/sqscr",
              "changeSysArg/toggle/sqscr",
              "changeSysArg/toggle/stayontop",
              "changeSysArg/false/stayontop",
              "changeSysArg/true/stayontop",
              "changeSysArg/toggle/stayontop",
              "changeSysArg/toggle/stopdeactive",
              "changeSysArg/false/stopdeactive",
              "changeSysArg/true/stopdeactive",
              "changeSysArg/toggle/stopdeactive"
            ]
          },
          {
            "key": "off_esccancel",
            "label": "off_esccancel",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/esccancel/off"
            ]
          },
          {
            "key": "off_facemode",
            "label": "off_facemode",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/facemode/off"
            ]
          },
          {
            "key": "off_fullscreen",
            "label": "off_fullscreen",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/fullscreen/off"
            ]
          },
          {
            "key": "off_item_icon",
            "label": "off_item_icon",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/item_icon/off"
            ]
          },
          {
            "key": "off_item_qmlk",
            "label": "off_item_qmlk",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/item_qmlk/off"
            ]
          },
          {
            "key": "off_item_toch",
            "label": "off_item_toch",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/item_toch/off"
            ]
          },
          {
            "key": "off_item_vprg",
            "label": "off_item_vprg",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/item_vprg/off"
            ]
          },
          {
            "key": "off_noeffect",
            "label": "off_noeffect",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/noeffect/off"
            ]
          }
        ],
        "pack": null
      },
      {
        "id": "2",
        "label": "游戏设置1",
        "mode": "panel",
        "rows": [
          {
            "key": "changeSysArg",
            "label": "changeSysArg",
            "type": "toggle",
            "bindings": [
              "changeSysArg/toggle/curmove",
              "changeSysArg/false/curmove",
              "changeSysArg/true/curmove",
              "changeSysArg/toggle/curmove",
              "changeSysArg/toggle/scanim",
              "changeSysArg/false/scanim",
              "changeSysArg/true/scanim",
              "changeSysArg/toggle/scanim",
              "changeSysArg/toggle/sqscr",
              "changeSysArg/false/sqscr",
              "changeSysArg/true/sqscr",
              "changeSysArg/toggle/sqscr",
              "changeSysArg/toggle/stayontop",
              "changeSysArg/false/stayontop",
              "changeSysArg/true/stayontop",
              "changeSysArg/toggle/stayontop",
              "changeSysArg/toggle/stopdeactive",
              "changeSysArg/false/stopdeactive",
              "changeSysArg/true/stopdeactive",
              "changeSysArg/toggle/stopdeactive"
            ]
          },
          {
            "key": "off_curmoveyes",
            "label": "off_curmoveyes",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/curmoveyes/off"
            ]
          },
          {
            "key": "off_filedclk",
            "label": "off_filedclk",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/filedclk/off"
            ]
          },
          {
            "key": "off_flowshow",
            "label": "off_flowshow",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/flowshow/off"
            ]
          },
          {
            "key": "off_hmou",
            "label": "off_hmou",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/hmou/off"
            ]
          },
          {
            "key": "off_hout",
            "label": "off_hout",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/hout/off"
            ]
          },
          {
            "key": "off_hsel",
            "label": "off_hsel",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/hsel/off"
            ]
          },
          {
            "key": "off_icpreview",
            "label": "off_icpreview",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/icpreview/off"
            ]
          },
          {
            "key": "off_readjump",
            "label": "off_readjump",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/readjump/off"
            ]
          },
          {
            "key": "off_readskip",
            "label": "off_readskip",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/readskip/off"
            ]
          },
          {
            "key": "off_suspend",
            "label": "off_suspend",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/suspend/off"
            ]
          },
          {
            "key": "on_curmoveyes",
            "label": "on_curmoveyes",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/curmoveyes/on"
            ]
          },
          {
            "key": "on_filedclk",
            "label": "on_filedclk",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/filedclk/on"
            ]
          },
          {
            "key": "on_flowshow",
            "label": "on_flowshow",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/flowshow/on"
            ]
          }
        ],
        "pack": null
      },
      {
        "id": "3",
        "label": "游戏设置2",
        "mode": "panel",
        "rows": [
          {
            "key": "0_skipst",
            "label": "0_skipst",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/skipst/0"
            ]
          },
          {
            "key": "0_txv_novo",
            "label": "0_txv_novo",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_novo/0"
            ]
          },
          {
            "key": "0_txv_other",
            "label": "0_txv_other",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_other/0"
            ]
          },
          {
            "key": "0_txv_voice",
            "label": "0_txv_voice",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/txv_voice/0"
            ]
          },
          {
            "key": "1_skipst",
            "label": "1_skipst",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/skipst/1"
            ]
          },
          {
            "key": "1_txv_novo",
            "label": "1_txv_novo",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_novo/1"
            ]
          },
          {
            "key": "1_txv_other",
            "label": "1_txv_other",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_other/1"
            ]
          },
          {
            "key": "1_txv_voice",
            "label": "1_txv_voice",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/txv_voice/1"
            ]
          },
          {
            "key": "2_skipst",
            "label": "2_skipst",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/skipst/2"
            ]
          },
          {
            "key": "2_txv_novo",
            "label": "2_txv_novo",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_novo/2"
            ]
          },
          {
            "key": "2_txv_other",
            "label": "2_txv_other",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/txv_other/2"
            ]
          },
          {
            "key": "2_txv_voice",
            "label": "2_txv_voice",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/txv_voice/2"
            ]
          },
          {
            "key": "changeBasicSlider",
            "label": "changeBasicSlider",
            "type": "button",
            "bindings": [
              "changeBasicSlider"
            ]
          },
          {
            "key": "off_dramatic",
            "label": "off_dramatic",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/dramatic/off"
            ]
          }
        ],
        "pack": null
      },
      {
        "id": "4",
        "label": "文本设置",
        "mode": "panel",
        "rows": [
          {
            "key": "0_autovwait",
            "label": "0_autovwait",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/autovwait/0"
            ]
          },
          {
            "key": "1_autovwait",
            "label": "1_autovwait",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/autovwait/1"
            ]
          },
          {
            "key": "2_autovwait",
            "label": "2_autovwait",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/autovwait/2"
            ]
          },
          {
            "key": "changeBasicSlider",
            "label": "changeBasicSlider",
            "type": "button",
            "bindings": [
              "changeBasicSlider"
            ]
          },
          {
            "key": "off_afterauto",
            "label": "off_afterauto",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/afterauto/off"
            ]
          },
          {
            "key": "off_afterskip",
            "label": "off_afterskip",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/afterskip/off"
            ]
          },
          {
            "key": "off_ctrlskip",
            "label": "off_ctrlskip",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/ctrlskip/off"
            ]
          },
          {
            "key": "off_nohwindow",
            "label": "off_nohwindow",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/nohwindow/off"
            ]
          },
          {
            "key": "off_skipall",
            "label": "off_skipall",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/skipall/off"
            ]
          },
          {
            "key": "onSpeedSliderChange",
            "label": "onSpeedSliderChange",
            "type": "slider",
            "bindings": [
              "onSpeedSliderChange",
              "onSpeedSliderChange",
              "onSpeedSliderChange",
              "onSpeedSliderChange",
              "onSpeedSliderChange"
            ]
          },
          {
            "key": "on_afterauto",
            "label": "on_afterauto",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/afterauto/on"
            ]
          },
          {
            "key": "on_afterskip",
            "label": "on_afterskip",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/afterskip/on"
            ]
          },
          {
            "key": "on_ctrlskip",
            "label": "on_ctrlskip",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/ctrlskip/on"
            ]
          },
          {
            "key": "on_nohwindow",
            "label": "on_nohwindow",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/nohwindow/on"
            ]
          }
        ],
        "pack": "assets/settings/option_4text__pack.png"
      },
      {
        "id": "5",
        "label": "音频设置",
        "mode": "panel",
        "rows": [
          {
            "key": "bgm",
            "label": "BGM",
            "type": "slider",
            "bindings": [
              "setAudioOnOff/bgm/toggle",
              "setAudioOnOff/bgm/0",
              "setAudioOnOff/bgm/1",
              "setAudioOnOff/bgm/toggle"
            ]
          },
          {
            "key": "bgv",
            "label": "ＢＧＶ（通常场景）",
            "type": "toggle",
            "bindings": [
              "setAudioOnOff/bgv/toggle",
              "setAudioOnOff/bgv/0",
              "setAudioOnOff/bgv/1",
              "setAudioOnOff/bgv/toggle"
            ]
          },
          {
            "key": "bgv2",
            "label": "bgv2",
            "type": "toggle",
            "bindings": [
              "setAudioOnOff/bgv2/toggle",
              "setAudioOnOff/bgv2/0",
              "setAudioOnOff/bgv2/1",
              "setAudioOnOff/bgv2/toggle"
            ]
          },
          {
            "key": "down",
            "label": "down",
            "type": "toggle",
            "bindings": [
              "setAudioOnOff/down/toggle",
              "setAudioOnOff/down/0",
              "setAudioOnOff/down/1",
              "setAudioOnOff/down/toggle"
            ]
          },
          {
            "key": "movie",
            "label": "影片",
            "type": "slider",
            "bindings": [
              "setAudioOnOff/movie/toggle",
              "setAudioOnOff/movie/0",
              "setAudioOnOff/movie/1",
              "setAudioOnOff/movie/toggle"
            ]
          },
          {
            "key": "off_lowprisysvo",
            "label": "off_lowprisysvo",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/lowprisysvo/off"
            ]
          },
          {
            "key": "off_mvaudiosample",
            "label": "off_mvaudiosample",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/mvaudiosample/off"
            ]
          },
          {
            "key": "off_voicecut",
            "label": "off_voicecut",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/voicecut/off"
            ]
          },
          {
            "key": "off_voiceeff",
            "label": "off_voiceeff",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/voiceeff/off"
            ]
          },
          {
            "key": "onAudioVolumeChange",
            "label": "onAudioVolumeChange",
            "type": "slider",
            "bindings": [
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange",
              "onAudioVolumeChange"
            ]
          },
          {
            "key": "onChVoiceVolumeChange",
            "label": "onChVoiceVolumeChange",
            "type": "slider",
            "bindings": [
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange",
              "onChVoiceVolumeChange"
            ]
          },
          {
            "key": "on_lowprisysvo",
            "label": "on_lowprisysvo",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/lowprisysvo/on"
            ]
          },
          {
            "key": "on_mvaudiosample",
            "label": "on_mvaudiosample",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/mvaudiosample/on"
            ]
          },
          {
            "key": "on_voicecut",
            "label": "on_voicecut",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/voicecut/on"
            ]
          }
        ],
        "pack": "assets/settings/option_5sound1__pack.png"
      },
      {
        "id": "6",
        "label": "确认信息",
        "mode": "panel",
        "rows": [
          {
            "key": "changeOnOffProp",
            "label": "changeOnOffProp",
            "type": "toggle",
            "bindings": [
              "changeOnOffProp/cf_backto/SystemConfig.askBackTo/toggle",
              "changeOnOffProp/cf_backto/SystemConfig.askBackTo/false",
              "changeOnOffProp/cf_backto/SystemConfig.askBackTo/true",
              "changeOnOffProp/cf_backto/SystemConfig.askBackTo/toggle",
              "changeOnOffProp/cf_copy/SystemConfig.askCopy/toggle",
              "changeOnOffProp/cf_copy/SystemConfig.askCopy/false",
              "changeOnOffProp/cf_copy/SystemConfig.askCopy/true",
              "changeOnOffProp/cf_copy/SystemConfig.askCopy/toggle",
              "changeOnOffProp/cf_delete/SystemConfig.askDelete/toggle",
              "changeOnOffProp/cf_delete/SystemConfig.askDelete/false",
              "changeOnOffProp/cf_delete/SystemConfig.askDelete/true",
              "changeOnOffProp/cf_delete/SystemConfig.askDelete/toggle",
              "changeOnOffProp/cf_dsave/SystemConfig.askDSave/toggle",
              "changeOnOffProp/cf_dsave/SystemConfig.askDSave/false",
              "changeOnOffProp/cf_dsave/SystemConfig.askDSave/true",
              "changeOnOffProp/cf_dsave/SystemConfig.askDSave/toggle",
              "changeOnOffProp/cf_exit/SystemConfig.askExit/toggle",
              "changeOnOffProp/cf_exit/SystemConfig.askExit/false",
              "changeOnOffProp/cf_exit/SystemConfig.askExit/true",
              "changeOnOffProp/cf_exit/SystemConfig.askExit/toggle",
              "changeOnOffProp/cf_flow/SystemConfig.askFlow/toggle",
              "changeOnOffProp/cf_flow/SystemConfig.askFlow/false",
              "changeOnOffProp/cf_flow/SystemConfig.askFlow/true",
              "changeOnOffProp/cf_flow/SystemConfig.askFlow/toggle",
              "changeOnOffProp/cf_init/SystemConfig.askInit/toggle",
              "changeOnOffProp/cf_init/SystemConfig.askInit/false",
              "changeOnOffProp/cf_init/SystemConfig.askInit/true",
              "changeOnOffProp/cf_init/SystemConfig.askInit/toggle",
              "changeOnOffProp/cf_initstand/SystemConfig.askInitStand/toggle",
              "changeOnOffProp/cf_initstand/SystemConfig.askInitStand/false",
              "changeOnOffProp/cf_initstand/SystemConfig.askInitStand/true",
              "changeOnOffProp/cf_initstand/SystemConfig.askInitStand/toggle",
              "changeOnOffProp/cf_jump/SystemConfig.askJump/toggle",
              "changeOnOffProp/cf_jump/SystemConfig.askJump/false",
              "changeOnOffProp/cf_jump/SystemConfig.askJump/true",
              "changeOnOffProp/cf_jump/SystemConfig.askJump/toggle",
              "changeOnOffProp/cf_load/SystemConfig.askLoad/toggle",
              "changeOnOffProp/cf_load/SystemConfig.askLoad/false",
              "changeOnOffProp/cf_load/SystemConfig.askLoad/true",
              "changeOnOffProp/cf_load/SystemConfig.askLoad/toggle",
              "changeOnOffProp/cf_move/SystemConfig.askMove/toggle",
              "changeOnOffProp/cf_move/SystemConfig.askMove/false",
              "changeOnOffProp/cf_move/SystemConfig.askMove/true",
              "changeOnOffProp/cf_move/SystemConfig.askMove/toggle",
              "changeOnOffProp/cf_next/SystemConfig.askNext/toggle",
              "changeOnOffProp/cf_next/SystemConfig.askNext/false",
              "changeOnOffProp/cf_next/SystemConfig.askNext/true",
              "changeOnOffProp/cf_next/SystemConfig.askNext/toggle",
              "changeOnOffProp/cf_nextscn/SystemConfig.askNextScn/toggle",
              "changeOnOffProp/cf_nextscn/SystemConfig.askNextScn/false",
              "changeOnOffProp/cf_nextscn/SystemConfig.askNextScn/true",
              "changeOnOffProp/cf_nextscn/SystemConfig.askNextScn/toggle",
              "changeOnOffProp/cf_overwrite/SystemConfig.askOverwrite/toggle",
              "changeOnOffProp/cf_overwrite/SystemConfig.askOverwrite/false",
              "changeOnOffProp/cf_overwrite/SystemConfig.askOverwrite/true",
              "changeOnOffProp/cf_overwrite/SystemConfig.askOverwrite/toggle",
              "changeOnOffProp/cf_prevscn/SystemConfig.askPrevScn/toggle",
              "changeOnOffProp/cf_prevscn/SystemConfig.askPrevScn/false",
              "changeOnOffProp/cf_prevscn/SystemConfig.askPrevScn/true",
              "changeOnOffProp/cf_prevscn/SystemConfig.askPrevScn/toggle",
              "changeOnOffProp/cf_qload/SystemConfig.askQLoad/toggle",
              "changeOnOffProp/cf_qload/SystemConfig.askQLoad/false",
              "changeOnOffProp/cf_qload/SystemConfig.askQLoad/true",
              "changeOnOffProp/cf_qload/SystemConfig.askQLoad/toggle",
              "changeOnOffProp/cf_qsave/SystemConfig.askQSave/toggle",
              "changeOnOffProp/cf_qsave/SystemConfig.askQSave/false",
              "changeOnOffProp/cf_qsave/SystemConfig.askQSave/true",
              "changeOnOffProp/cf_qsave/SystemConfig.askQSave/toggle",
              "changeOnOffProp/cf_resume/SystemConfig.askResume/toggle",
              "changeOnOffProp/cf_resume/SystemConfig.askResume/false",
              "changeOnOffProp/cf_resume/SystemConfig.askResume/true",
              "changeOnOffProp/cf_resume/SystemConfig.askResume/toggle",
              "changeOnOffProp/cf_save/SystemConfig.askSave/toggle",
              "changeOnOffProp/cf_save/SystemConfig.askSave/false",
              "changeOnOffProp/cf_save/SystemConfig.askSave/true",
              "changeOnOffProp/cf_save/SystemConfig.askSave/toggle",
              "changeOnOffProp/cf_swap/SystemConfig.askSwap/toggle",
              "changeOnOffProp/cf_swap/SystemConfig.askSwap/false",
              "changeOnOffProp/cf_swap/SystemConfig.askSwap/true",
              "changeOnOffProp/cf_swap/SystemConfig.askSwap/toggle",
              "changeOnOffProp/cf_title/SystemConfig.askTitle/toggle",
              "changeOnOffProp/cf_title/SystemConfig.askTitle/false",
              "changeOnOffProp/cf_title/SystemConfig.askTitle/true",
              "changeOnOffProp/cf_title/SystemConfig.askTitle/toggle",
              "changeOnOffProp/cf_vsave/SystemConfig.askVSave/toggle",
              "changeOnOffProp/cf_vsave/SystemConfig.askVSave/false",
              "changeOnOffProp/cf_vsave/SystemConfig.askVSave/true",
              "changeOnOffProp/cf_vsave/SystemConfig.askVSave/toggle"
            ]
          },
          {
            "key": "reset",
            "label": "reset",
            "type": "slider",
            "bindings": [
              "reset"
            ]
          },
          {
            "key": "setAllConfirm",
            "label": "setAllConfirm",
            "type": "slider",
            "bindings": [
              "setAllConfirm/0",
              "setAllConfirm/1"
            ]
          }
        ],
        "pack": "assets/settings/option_6dialog__pack.png"
      },
      {
        "id": "7",
        "label": "鼠标",
        "mode": "panel",
        "rows": [
          {
            "key": "off_gsenable",
            "label": "off_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/off"
            ]
          },
          {
            "key": "off_gsflick",
            "label": "off_gsflick",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/gsflick/off"
            ]
          },
          {
            "key": "off_gsmouse",
            "label": "off_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/off"
            ]
          },
          {
            "key": "on_gsenable",
            "label": "on_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/on"
            ]
          },
          {
            "key": "on_gsflick",
            "label": "on_gsflick",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/gsflick/on"
            ]
          },
          {
            "key": "on_gsmouse",
            "label": "on_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/on"
            ]
          },
          {
            "key": "reset",
            "label": "reset",
            "type": "slider",
            "bindings": [
              "reset"
            ]
          },
          {
            "key": "toggle_gsenable",
            "label": "toggle_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/toggle",
              "setBasicOptionValue/gsenable/toggle"
            ]
          },
          {
            "key": "toggle_gsflick",
            "label": "toggle_gsflick",
            "type": "toggle",
            "bindings": [
              "setBasicOptionValue/gsflick/toggle",
              "setBasicOptionValue/gsflick/toggle"
            ]
          },
          {
            "key": "toggle_gsmouse",
            "label": "toggle_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/toggle",
              "setBasicOptionValue/gsmouse/toggle"
            ]
          }
        ],
        "pack": "assets/settings/option_7mouse__pack.png"
      },
      {
        "id": "8",
        "label": "键盘",
        "mode": "panel",
        "rows": [
          {
            "key": "reset",
            "label": "reset",
            "type": "slider",
            "bindings": [
              "reset"
            ]
          },
          {
            "key": "setKeyBind",
            "label": "setKeyBind",
            "type": "slider",
            "bindings": [
              "setKeyBind/0/auto",
              "setKeyBind/1/auto",
              "setKeyBind/0/backone",
              "setKeyBind/1/backone",
              "setKeyBind/0/backskip",
              "setKeyBind/1/backskip",
              "setKeyBind/0/click",
              "setKeyBind/1/click",
              "setKeyBind/0/ctrl",
              "setKeyBind/1/ctrl",
              "setKeyBind/0/dsave",
              "setKeyBind/1/dsave",
              "setKeyBind/0/hide",
              "setKeyBind/1/hide",
              "setKeyBind/0/load",
              "setKeyBind/1/load",
              "setKeyBind/0/log",
              "setKeyBind/1/log",
              "setKeyBind/0/next",
              "setKeyBind/1/next",
              "setKeyBind/0/nextscn",
              "setKeyBind/1/nextscn",
              "setKeyBind/0/option",
              "setKeyBind/1/option",
              "setKeyBind/0/pagedown",
              "setKeyBind/1/pagedown",
              "setKeyBind/0/pageup",
              "setKeyBind/1/pageup",
              "setKeyBind/0/panic",
              "setKeyBind/1/panic",
              "setKeyBind/0/prev",
              "setKeyBind/1/prev",
              "setKeyBind/0/prevscn",
              "setKeyBind/1/prevscn",
              "setKeyBind/0/qload",
              "setKeyBind/1/qload",
              "setKeyBind/0/qsave",
              "setKeyBind/1/qsave",
              "setKeyBind/0/qvsave",
              "setKeyBind/1/qvsave",
              "setKeyBind/0/save",
              "setKeyBind/1/save",
              "setKeyBind/0/scnchart",
              "setKeyBind/1/scnchart",
              "setKeyBind/0/screen",
              "setKeyBind/1/screen",
              "setKeyBind/0/skip",
              "setKeyBind/1/skip",
              "setKeyBind/0/snapshot",
              "setKeyBind/1/snapshot",
              "setKeyBind/0/title",
              "setKeyBind/1/title",
              "setKeyBind/0/volume",
              "setKeyBind/1/volume",
              "setKeyBind/0/vreplay",
              "setKeyBind/1/vreplay",
              "setKeyBind/0/vsave",
              "setKeyBind/1/vsave"
            ]
          },
          {
            "key": "showKeyBind",
            "label": "showKeyBind",
            "type": "button",
            "bindings": [
              "showKeyBind"
            ]
          }
        ],
        "pack": "assets/settings/option_8keyboard1__pack.png"
      },
      {
        "id": "9",
        "label": "游戏手柄",
        "mode": "panel",
        "rows": [
          {
            "key": "off_engamepad",
            "label": "off_engamepad",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/engamepad/off"
            ]
          },
          {
            "key": "off_gsenable",
            "label": "off_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/off"
            ]
          },
          {
            "key": "off_gsflick",
            "label": "off_gsflick",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/gsflick/off"
            ]
          },
          {
            "key": "off_gsmouse",
            "label": "off_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/off"
            ]
          },
          {
            "key": "on_engamepad",
            "label": "on_engamepad",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/engamepad/on"
            ]
          },
          {
            "key": "on_gsenable",
            "label": "on_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/on"
            ]
          },
          {
            "key": "on_gsflick",
            "label": "on_gsflick",
            "type": "button",
            "bindings": [
              "setBasicOptionValue/gsflick/on"
            ]
          },
          {
            "key": "on_gsmouse",
            "label": "on_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/on"
            ]
          },
          {
            "key": "reassignGamePadButtons",
            "label": "reassignGamePadButtons",
            "type": "button",
            "bindings": [
              "reassignGamePadButtons"
            ]
          },
          {
            "key": "reset",
            "label": "reset",
            "type": "slider",
            "bindings": [
              "reset"
            ]
          },
          {
            "key": "toggle_engamepad",
            "label": "toggle_engamepad",
            "type": "toggle",
            "bindings": [
              "setBasicOptionValue/engamepad/toggle",
              "setBasicOptionValue/engamepad/toggle"
            ]
          },
          {
            "key": "toggle_gsenable",
            "label": "toggle_gsenable",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsenable/toggle",
              "setBasicOptionValue/gsenable/toggle"
            ]
          },
          {
            "key": "toggle_gsflick",
            "label": "toggle_gsflick",
            "type": "toggle",
            "bindings": [
              "setBasicOptionValue/gsflick/toggle",
              "setBasicOptionValue/gsflick/toggle"
            ]
          },
          {
            "key": "toggle_gsmouse",
            "label": "toggle_gsmouse",
            "type": "slider",
            "bindings": [
              "setBasicOptionValue/gsmouse/toggle",
              "setBasicOptionValue/gsmouse/toggle"
            ]
          }
        ],
        "pack": "assets/settings/option_9gamepad__pack.png"
      }
    ],
    "help": "assets/locale/help_opt_cn.txt",
    "footer": {
      "back_title": "标题画面",
      "back_game": "游戏画面"
    },
    "sources": [
      "uipsd/option__bg0 + option__pack",
      "option_0simple 2×5 热区",
      "locale/cn/help_opt_cn.txt"
    ],
    "frame": {
      "x": 109,
      "y": 120,
      "w": 1701,
      "h": 839
    },
    "pixel_ui_default": true
  },
  "load": {
    "style": "file-load",
    "bg": "assets/load/bg.png",
    "pack": "assets/load/pack.png",
    "title": "DATA LOAD",
    "slots": 12,
    "help": "assets/locale/help_file_cn.txt",
    "sources": [
      "load.ks",
      "uipsd/file_load.pbd",
      "main/savelist.csv"
    ]
  },
  "flowchart": {
    "style": "scnchart",
    "bg": "assets/flowchart/bg.png",
    "pack": "assets/flowchart/pack.png",
    "title": "流程图",
    "nodes": [
      "序章",
      "第1章",
      "第2章",
      "第3章",
      "第4章",
      "终章",
      "After",
      "返回标题"
    ],
    "help": "assets/locale/help_flow_cn.txt",
    "sources": [
      "scnchart.ks",
      "uipsd/scnchart.pbd",
      "main/scnchartdata.tjs"
    ]
  },
  "cg": {
    "style": "extra-cg",
    "bg": "assets/cg/bg.png",
    "pack": "assets/cg/extra_locale_cn__pack.png",
    "title": "ＣＧ欣赏",
    "items": [
      "#サムネール",
      ":",
      "thum_ev101",
      "thum_ev102",
      "thum_ev103",
      "thum_ev105",
      "thum_ev104",
      "thum_ev106",
      "thum_ev108",
      "thum_ev123",
      "thum_ev107",
      "thum_ev109",
      "thum_ev122",
      "thum_ev110",
      "thum_ev121",
      "thum_ev111"
    ],
    "help": "assets/locale/help_extra_cn.txt",
    "sources": [
      "uipsd/extra_cg*.pbd",
      "main/cglist.csv",
      "locale/cn/help_extra_cn.txt"
    ]
  },
  "manifest": {
    "packs": 71,
    "hotspots": 53,
    "title_bgs": 8,
    "locale": 23
  }
};
