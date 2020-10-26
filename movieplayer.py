import time
from rpi_ws281x import PixelStrip, Color
import argparse
import cv2

# LED strip configuration:
LED_COUNT = 256*3        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

MOVIE_HEIGHT = 16
MOVIE_WIDTH = 24

def clear():
    for k in range(LED_COUNT):
        strip.setPixelColor(k, Color(0,0,0))
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='movie file')    # 必須の引数を追加
    parser.add_argument('-c', '--clear', action='store_true',
                        help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                       LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    video_path = "/home/pi/Documents/EIPD/rpi_neopixel_python/movie/"+args.file
    cap = cv2.VideoCapture(video_path)
    FPS = cap.get(cv2.CAP_PROP_FPS)

    pixel_values = [[
        0 for i2 in range(LED_COUNT)] for i1 in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))]
    # pixel_values[frame][i][R,G,B]の構造

    
    print('---------------------------------')
    print('MOVIE: {0}'.format(args.file))
    print('FPS: {0}'.format(FPS))
    print('LENGTH: {0} sec'.format(cap.get(cv2.CAP_PROP_FRAME_COUNT)/FPS))
    print('---------------------------------')

    # 動画の読み込み
    frame_index = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # readImage
            # Change the order to RGB
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for i in range(MOVIE_HEIGHT):
                for j in range(MOVIE_WIDTH):
                    if ((j%2) == 0):
                      
                        pixel_values[frame_index][j * MOVIE_HEIGHT + i] = img[i, j]
                 
                        pixel_values[frame_index][j * MOVIE_HEIGHT + i + (LED_COUNT//2)] = img[i, j]
                    else:
                        pixel_values[frame_index][(j * MOVIE_HEIGHT) + (MOVIE_HEIGHT-i-1)] = img[i, j]
     
                        pixel_values[frame_index][(j * MOVIE_HEIGHT) + (MOVIE_HEIGHT-i-1) + (LED_COUNT//2)] = img[i, j]
            frame_index += 1
        else:
            break

    print('Press Ctrl-C to quit.')
    
    try:
        # 再生
        print('Start playing')
        while(True):
            start = time.time()
            for i in range(len(pixel_values)):
                for k in range(LED_COUNT):
                    strip.setPixelColor(k, Color(int(pixel_values[i][k][0]), int(
                        pixel_values[i][k][1]), int(pixel_values[i][k][2])))
                strip.show()
                #時間合わせ
                elapsed_time = time.time() - start
                if((1/FPS * (i+1)) > elapsed_time):
                    time.sleep((1/FPS) * (i+1)-elapsed_time)
            print('---------------------------------')
            print("playing ended.\nActual time:{0}".format(elapsed_time) + "[sec]")
            clear()
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        clear()
            
            
