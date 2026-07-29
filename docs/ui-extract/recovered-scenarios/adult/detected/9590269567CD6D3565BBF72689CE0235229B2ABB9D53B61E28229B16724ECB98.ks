*start
;アフター分岐
[eval exp="delete tf.start_storage"]
[eval exp="delete tf.start_target"]
[macro name="_afterstory"]
[set name='tf.start_storage' value='&"x_"+mp.storage']
[return target=*jump]
[endmacro]

;アフター分岐
[_afterstory storage="【乃愛】16（H4）.ks"		cond='tf.afterstory=="noa"']
[_afterstory storage="【天音】14（after）.ks"		cond='tf.afterstory=="ama"']
[_afterstory storage="【来海】アフター.ks"		cond='tf.afterstory=="kur"']
[_afterstory storage="【かぐ耶】20.ks"			cond='tf.afterstory=="kag"']
[_afterstory storage="E21アフターH.ks"			cond='tf.afterstory=="ori"']
[_afterstory storage="【風実花】08（after）.ks"		cond='tf.afterstory=="fum"']

@return

*jump
[eval exp="delete tf.afterstory"]
[exit storage="start.ks" target="*jump"]
