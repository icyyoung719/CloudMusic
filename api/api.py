from music_downloader import MusicDownloader

def download_playlist(playlist_url, filepath):
    downloader = MusicDownloader()
    downloader.download_playlist(playlist_url, filepath)

def download_album(album_url, filepath):
    downloader = MusicDownloader()
    downloader.download_album(album_url, filepath)

def download_song(song_url, filepath):
    downloader = MusicDownloader()
    downloader.download_song(song_url, filepath)