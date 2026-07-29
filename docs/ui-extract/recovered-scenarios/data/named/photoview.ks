*start
*start_game
	[sysse   name="photoview.click"]
	[history enabled=false]
	[panel class=PhotoViewPanel]
*back
;	[sysse   name="photoview.rclick"]
	[syshook name="photoview.back"]

*game
	[sysjump from="photoview" to="game" back]

*return
	[sysrestore]
	[return]

*sysfrom_game
	[sysjump from="game"  to="photoview"]
