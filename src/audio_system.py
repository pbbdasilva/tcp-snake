import vlc
import os

CURR_DIR = os.path.abspath(os.path.dirname( __file__ ) )
PARENT_DIR = os.path.abspath( os.path.join(CURR_DIR, "..") )
MENU_SONG = os.path.join(PARENT_DIR, "audio/whatsyourask.mp3")
GAME_SONG = os.path.join(PARENT_DIR, "audio/oneor0.mp3")
LOSER_SONG = os.path.join(PARENT_DIR, "sadness_and_sorrow.mp3")

class Background_music:
    def __init__( self ):
        self.curr_song = [ MENU_SONG, GAME_SONG, LOSER_SONG ]
        self.music_on = True
        self.song = vlc.MediaListPlayer()
        self.song.set_playback_mode( vlc.PlaybackMode.loop )
        self.player = vlc.Instance()

    def play( self, idx = 0 ):
        if(not self.music_on ): return vlc.State.Stopped

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
        self.music_on = False
