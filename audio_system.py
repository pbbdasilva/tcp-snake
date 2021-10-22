import vlc
import os
import time

MENU_SONG = os.path.join('audio', 'hello.mp3')

class Background_music:
    def __init__( self ):
        self.curr_song = [ MENU_SONG ]
        self.song = vlc.MediaListPlayer()
        self.song.set_playback_mode( vlc.PlaybackMode.loop )
        self.player = vlc.Instance()

    def play( self, idx = 0 ):
        music_list = self.player.media_list_new()
        music = self.player.media_new( self.curr_song[ idx ] )
        music_list.add_media( music )
        self.song.set_media_list( music_list )
        self.song.play()

    def halt( self ):
        self.song.stop()

def main():
    music = Background_music()

    time.sleep(15)

    music.stop()

if __name__ == '__main__':
    main()