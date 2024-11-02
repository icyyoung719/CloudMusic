import os
from api.config import PROJECT_DIR, DEFAULT_SONG_URL, DEFAULT_ALBUM_URL, DEFAULT_PLAYLIST_URL
from api.music_downloader import MusicDownloader


def get_filepath():
    """
    Prompts the user for a save directory and subfolder. If none is provided, defaults to the user's Music folder.
    """
    filepath = input('请输入要保存的文件路径,为空则默认为系统音乐文件夹: ')
    if not filepath:
        user_profile = os.environ.get('USERPROFILE', '/')
        filepath = os.path.join(user_profile, 'Music')

    dir_name = input('请输入要保存的子文件夹名称,为空则默认为根文件夹: ')
    if dir_name:
        filepath = os.path.join(filepath, dir_name)

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    return filepath


def download_content(downloader, type, filepath, content_id):
    """
    Downloads content based on the user's choice (playlist, album, or song) and saves it to the specified filepath.
    """
    if type == '1':
        real_url = DEFAULT_SONG_URL + content_id
        downloader.download_song(real_url, filepath)
    elif type == '2':
        real_url = DEFAULT_PLAYLIST_URL + content_id
        downloader.download_playlist(real_url, filepath)
    elif type == '3':
        real_url = DEFAULT_ALBUM_URL + content_id
        downloader.download_album(real_url, filepath)

def main():
    downloader = MusicDownloader()
    while True:
        print('下载:单曲内容,输入1;  歌单内容,输入2;  专辑内容,输入3;  退出按q')
        type = input('请输入要下载的内容类型编号: ')
        if type == 'q':
            print("程序退出")
            break
        elif type not in ["1", "2", "3"]:
            print('Warning:请输入正确编号')
            continue

        filepath = get_filepath()
        content_id = input('请输入(歌单/专辑/单曲)id: ')
        download_content(downloader, type, filepath, content_id)


if __name__ == '__main__':
    main()
