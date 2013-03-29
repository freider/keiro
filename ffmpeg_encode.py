import subprocess


class Video(object):
    """Encodes images to a video file
    """
    def __init__(self, path, frame_rate, frame_size=None):
        """"Create a new Video object

        If `frame_size` isn't set, it will be automatically set to the
        size of the first input video frame.
        """
        self.path = path
        self.frames = 0
        self.frame_size = frame_size
        self.frame_rate = frame_rate

        if self.frame_size:
            self._init()

    def _init(self):
        """Opens video pipe.

        Requires self.frame_size to be set
        """
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

    def add_frame(self, image):
        """ Adds a video frame to the video

        @param
        image: a PIL-compatible Image object
        """
        if self.frame_size is None:
            self.frame_size = image.size
            self._init()
        else:
            assert self.frame_size == image.size

        self._pipe.stdin.write(image.tostring())
        self._last_frame = image

        self.frames += 1

    def close(self):
        self._pipe.stdin.close()
        self._pipe.wait()


if __name__ == "__main__":
    import Image

    frame_rate = 10
    mode = "RGB"
    size = (640, 480)
    red = Image.new(mode, size, (255, 0, 0))
    blue = Image.new(mode, size, (0, 0, 255))

    video = Video("videos/test.mp4", frame_rate, size)
    red.show()
    time.sleep(10)

    for i in xrange(24):
        video.add_frame(blue)
        video.add_frame(red)

    video.close()
