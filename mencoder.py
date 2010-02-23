import Image
import tempfile
import os
import shutil
import unittest
import subprocess
import shlex

FRAME_FORMAT = "png"
FRAME_EXTENSION = ".png"
COMMAND_PATTERN = """mencoder mf://{frames} -mf w={width}:h={height}:fps={framerate}:type={format} -ovc \
				lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o {outfile}"""
	
class Encoder(object):
	"""Encodes images to a movie file. Requires a lot of temporary hard drive space"""
	def __init__(self):
		self._tmpdir = tempfile.mkdtemp()
		print("Tmpdir: " + self._tmpdir)
		self.frames = 0
		self.dim = None
		
	def add_frame(self, image):
		if self.frames == 0:
			self.dim = image.size
		else:
			assert(self.dim == image.size) #TODO: clean up after error!
			
		self.frames += 1
		filename = os.path.join(self._tmpdir, "frame%05d%s"%(self.frames, FRAME_EXTENSION))
		image.save(filename)
		
	def encode(self, framerate, path):
		kwargs = dict(frames = os.path.join(self._tmpdir, "*"+FRAME_EXTENSION),
			width = self.dim[0],
			height = self.dim[1],
			format = FRAME_FORMAT,
			framerate = framerate,
			outfile = path)

		cmd = COMMAND_PATTERN.format(**kwargs)
		process = subprocess.Popen(shlex.split(cmd))
		process.communicate()
		
	def cleanup(self):
		if self._tmpdir != None:
			shutil.rmtree(self._tmpdir)
		self._tmpdir = None
		
	
class TestEncoder(unittest.TestCase):
	def testencode(self):
		enc = Encoder()
		size = (640,480)
		mode = "RGB"
		framerate = 2
		red = Image.new(mode, size, (255, 0, 0))
		blue = Image.new(mode, size, (0, 0, 255))
		
		enc.add_frame(red)
		enc.add_frame(blue)
		enc.add_frame(red)
		enc.add_frame(blue)
		
		enc.encode(framerate, "/Users/elias/Desktop/test.avi") #TODO: more flexible testing
		enc.cleanup()
	
if __name__ == "__main__":
	unittest.main()