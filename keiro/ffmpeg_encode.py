import subprocess
import os


def available():
    with open(os.devnull, 'w') as devnull:
        try:
            subprocess.Popen(["ffmpeg", "-version"], stderr=subprocess.STDOUT, stdout=devnull)
        except OSError:
            return False
    return True


class Video(object):
    """Encodes images to a video file
    """
    def __init__(self, path, frame_rate, frame_size):
        """Create a new Video output stream

        Adding frames using `add_frame()` and make sure to close the
        video stream using `close()` when finished to make sure the
        video file isn't corrupted.
        """
        self.path = path
        self.frames = 0
        self.frame_size = frame_size
        self.frame_rate = frame_rate

        size_string = '{0}x{1}'.format(*self.frame_size)
        self._pipe = cmd = [
            'ffmpeg',
            #'-loglevel', 'quiet',
            '-y',  # overwrite output files
            '-pix_fmt', 'rgb24',
            '-f', 'rawvideo',
            '-s', size_string,
            '-i', '-',  # input from stdin
            '-an',  # no audio
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            '-r', str(self.frame_rate),
            '-vcodec', 'h264',
            #'-profile:v', 'main',  # for quicktime compatibility
            self.path,
        ]
        self._pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def add_frame(self, image_string):
        """ Adds a video frame to the video

        @param
        image: a binary string with an image in (24bit) RGB format
        """
        self._pipe.stdin.write(image_string)
        self.frames += 1

    def close(self):
        self._pipe.stdin.close()
        self._pipe.wait()


if __name__ == "__main__":
    import Image

    frame_rate = 10
    mode = "RGB"
    size = (640, 480)
    red = Image.new(mode, size, (255, 0, 0)).tostring()
    blue = Image.new(mode, size, (0, 0, 255)).tostring()

    video = Video("videos/video_test.mp4", frame_rate, size)

    for i in xrange(24):
        video.add_frame(blue)
        video.add_frame(red)

    video.close()
