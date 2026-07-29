@title name=&aboutDialogConfig.title
@linemode mode=none
@clickskip enabled=false
@rclick    enabled=false
@if exp="getExistImageName(aboutDialogConfig.storage) !== void"
@position left=0 top=0 width=&kag.aboutWidth height=&kag.aboutHeight transparent=true opacity=255 marginl=0 margint=&aboutDialogConfig.top marginr=0 marginb=&-aboutDialogConfig.size*2 frame=&aboutDialogConfig.storage
@else
@position left=0 top=0 width=&kag.aboutWidth height=&kag.aboutHeight transparent=true opacity=0 marginl=0 margint=&aboutDialogConfig.top marginr=0 marginb=&-aboutDialogConfig.size*2 color=&(aboutDialogConfig.bgcolor|0xFF000000)
@endif
@backlay
@current page=back
@if exp='aboutDialogConfig.drawtexttag!=""'
@eval exp=CustomDrawLayerText(this.current,("@'"+aboutDialogConfig.versionstring.escape()+"'")!,aboutDialogConfig.drawtexttag)
@jump target=*done
@endif
@defstyle autoreturn=false linesize=1 linespacing=&aboutDialogConfig.linespacing pitch=&aboutDialogConfig.pitch
@deffont  size=&aboutDialogConfig.size face=&aboutDialogConfig.face color=&aboutDialogConfig.color shadow=&aboutDialogConfig.shadow shadowcolor=&aboutDialogConfig.shadowcolor edge=&aboutDialogConfig.edge edgecolor=&aboutDialogConfig.edgecolor
@er
@style align=&aboutDialogConfig.align
@delay speed=nowait
@eval exp=tf.versionstring=("@'"+aboutDialogConfig.versionstring.escape()+"'")!.split("\n")
*loop
@eval exp=tf.versionline=tf.versionstring.shift()
@if exp="aboutDialogConfig.pitch==0"
[ch text=&tf.versionline]
@else
[emb exp=&tf.versionline]
@endif
@jump target=*done cond=!tf.versionstring.count
@r
@jump target=*loop
*done
@rclick enabled jump storage="" target=*exit
@trans method=crossfade time=&aboutDialogConfig.versionfade
@clickskip enabled=true
@beginskip
@wt canskip=true
@waitclick
@endskip
*exit
@close
