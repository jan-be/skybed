import threading

from ma.subscriber import subscribe
from ma.uas_position_updater import loop_update_post_position

if __name__ == '__main__':
    threading.Thread(target=loop_update_post_position).start()
    threading.Thread(target=subscribe).start()