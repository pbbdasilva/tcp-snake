from posixpath import dirname
import vlc
import os
import time

CURR_DIR = os.path.abspath(os.path.dirname( __file__ ) )
PARENT_DIR = os.path.abspath( os.path.join(CURR_DIR, "..") )
MENU_SONG = os.path.join(PARENT_DIR, "audio/hello.mp3")
GAME_SONG = os.path.join(PARENT_DIR, "audio/oneor0.mp3")

class Background_music:
    def __init__( self ):
        self.curr_song = [ MENU_SONG, GAME_SONG ]
        self.song = vlc.MediaListPlayer()
        self.song.set_playback_mode( vlc.PlaybackMode.loop )
        self.player = vlc.Instance()

    def play( self, idx = 0 ):
        music_list = self.player.media_list_new()
        music = self.player.media_new( self.curr_song[ idx ] )
        music_list.add_media( music )
        self.song.set_media_list( music_list )

        if(self.song.is_playing()):
            self.song.next()
        else:
            self.song.play()

    def halt( self ):
        self.song.stop()
