from moviepy.editor import *
import cv2 as cv2
import matplotlib.pyplot as plt
import numpy as np
import os

class MemeGenerator:   

    input_clip_path = None
    start_time = None
    climax_time = None
    bg_climax = 4

    tobecontinued_imgtext = None
    video_clip = None
    audio_clip = None

    asset_path = os.path.abspath(os.path.dirname(__file__))
    tobecontinued_bgm_path = os.path.join(asset_path, 'assets', 'toBeContinuedMeme', 'climax_tobecontinued.mp3')
    tobecontinued_imgtext_path = os.path.join(asset_path, 'assets', 'toBeContinuedMeme','small-tobecontinued.png')

    def __init__(self, input_clip, start_time, climax_time):
        self.input_clip_path = input_clip
        self.start_time = start_time
        self.climax_time = climax_time
        
        self.tobecontinued_imgtext = cv2.imread(self.tobecontinued_imgtext_path, cv2.IMREAD_UNCHANGED) # bgra channel
        self.video_clip = VideoFileClip(self.input_clip_path)
        self.audio_clip = AudioFileClip(self.tobecontinued_bgm_path)


    # process the intro
    # intro starts at the start_time and then concatenate to the climax
    # further development for option to add the tobecontiued_bgm intro in this clip
    def create_intro(self):
        intro_clip = self.video_clip.subclip(self.start_time, self.climax_time - self.bg_climax)
        return intro_clip


    # process the climax
    # climax intro
    # to process before the word to be continued appeared
    def create_climax_intro(self):
        climax_intro = self.video_clip.subclip(self.climax_time - self.bg_climax, self.climax_time)
        climax_intro_bgm = self.audio_clip.subclip(0,4)
        climax_intro_bgm = CompositeAudioClip([climax_intro.audio, climax_intro_bgm])
        climax_intro.audio = climax_intro_bgm
        return climax_intro


    # climax end
    # change the color and add it with the tobecontinued_bgm
    # further development for option to zoom after 3 second music kicks
    # zoom to certain point 
    def create_climax_end(self):
        audio_duration = self.audio_clip.duration - 4
        climax_end_bgm = self.audio_clip.subclip(4)
        climax_end_bg = self.video_clip.get_frame(self.climax_time).copy()
        # processing the color of the image
        # make it slightly reddish
        climax_end_bg[:, :, 0] = climax_end_bg[:, :, 0] * 1 
        climax_end_bg[:, :, 1] = climax_end_bg[:, :, 1] * 0.4 
        climax_end_bg[:, :, 2] = climax_end_bg[:, :, 1] * 0.1 
        climax_end_bg = np.clip(climax_end_bg, 0, 255)
        # append to be continued image
        # configuring the size of the overlay image
        # the size is always 20 percent from the height and 50 percent of the width
        # need to be resized so that it could fit the image container
        imgtext_height = int(len(climax_end_bg) * 0.2)
        imgtext_width = int(len(climax_end_bg[0]) * 0.5)
        tobecontinued_imgtext_mod = cv2.resize(self.tobecontinued_imgtext, (imgtext_width, imgtext_height))
        # paste the image to the bottom right
        # it's a .png so we have to concerned about the alpha channel
        for i in range(len(tobecontinued_imgtext_mod)):
            for j in range(len(tobecontinued_imgtext_mod[0])):
                if tobecontinued_imgtext_mod[-i, -j, 3] != 0:
                    climax_end_bg[-i, -j, 0] = tobecontinued_imgtext_mod[-i, -j, 0]
                    climax_end_bg[-i, -j, 1] = tobecontinued_imgtext_mod[-i, -j, 1]
                    climax_end_bg[-i, -j, 2] = tobecontinued_imgtext_mod[-i, -j, 2]
            # climax_end_bg[-imgtext_height::, -imgtext_width::] = tobecontinued_imgtext_mod[:,:,0:3]

        # plt.imshow(climax_end_bg)
        climax_end = ImageClip(climax_end_bg, duration=audio_duration)
        climax_end.fps = self.video_clip.fps
        climax_end.audio = climax_end_bgm
        return climax_end


    # write output_video
    def write_video(self, intro_clip, climax_intro, climax_end, output_path):
        output_clip = concatenate_videoclips([intro_clip, climax_intro, climax_end])
        output_clip.write_videofile(output_path, 
                                threads=8, 
                                preset='ultrafast', 
                                fps=24)
    # print(video_clip.duration)


    def create_meme(self, output_dir):
        intro_clip = self.create_intro()
        climax_intro = self.create_climax_intro()
        climax_end = self.create_climax_end()
        self.write_video(intro_clip, climax_intro, climax_end, output_dir)


    if __name__ == "__main__":
        

        create_meme()