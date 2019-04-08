import time
import _rpi_ws281x as ws

# LED configuration.
LED_CHANNEL    = 0
LED_COUNT      = 80         # How many LEDs to light.
LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM    = 10         # DMA channel to use, can be 0-14.
LED_GPIO       = 18         # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN
                            # transistor as a 3.3V->5V level converter.  Keep at 0
                            # for a normal/non-inverted signal.

# Create a ws2811_t structure from the LED configuration.
# Note that this structure will be created on the heap so you need to be careful
# that you delete its memory by calling delete_ws2811_t when it's not needed.
leds = ws.new_ws2811_t()

# Initialize all channels to off
for channum in range(2):
    channel = ws.ws2811_channel_get(leds, channum)
    ws.ws2811_channel_t_count_set(channel, 0)
    ws.ws2811_channel_t_gpionum_set(channel, 0)
    ws.ws2811_channel_t_invert_set(channel, 0)
    ws.ws2811_channel_t_brightness_set(channel, 0)

channel = ws.ws2811_channel_get(leds, LED_CHANNEL)

ws.ws2811_channel_t_count_set(channel, LED_COUNT)
ws.ws2811_channel_t_gpionum_set(channel, LED_GPIO)
ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)

ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)

# Initialize library with LED configuration.
resp = ws.ws2811_init(leds)
if resp != ws.WS2811_SUCCESS:
    message = ws.ws2811_get_return_t_str(resp)
    raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, message))

def render():
    resp = ws.ws2811_render(leds)
    if resp != ws.WS2811_SUCCESS:
        message = ws.ws2811_get_return_t_str(resp)
        raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, message))

RPS = 6.0   # Rotations per second
RDIV = 40   # Number of radial divisions
THDIV = 72  # Number of angle divisions

from matrix import matrix

def wheel(position):
    if position < 85:
        return ((position * 3) << 16) + ((255 - position * 3) << 8)
    elif position < 170:
        position -= 85
        return ((255 - position * 3) << 16) + (position * 3)
    else:
        position -= 170
        return ((position * 3) << 8) + (255 - position * 3)

def rainbow(iterations, strip, wait):
    for j in range(256 * iterations):
        for i in range(LED_COUNT):
            ws.ws2811_led_set(channel, i, wheel((i + j) & 255))
        render()
        time.sleep(wait)

def rainbow_cycle(iterations, strip, wait):
    for j in range(256 * iterations):
        for i in range(LED_COUNT):
            ws.ws2811_led_set(channel, i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        render()
        time.sleep(wait)

def disp_image(iterations, matrix, loop=False):
    thfactor = 360 // THDIV     # Angle per division
    elapsed_time = 0            # Time elapsed in each iteration
    theta = 0                   # Current angle of blades

    while iterations > 0:
        theta += int(RPS * elapsed_time * 360)
        theta %= 360
        elapsed_time = time.perf_counter()

        for i in range(LED_COUNT//2, LED_COUNT):
            color = matrix[theta//thfactor][i - LED_COUNT//2]
            ws.ws2811_led_set(channel, i, color)
        
        for i in range(0, LED_COUNT//2):
            color = matrix[((theta//thfactor) + (180//thfactor)) % THDIV][LED_COUNT//2 - i - 1]
            ws.ws2811_led_set(channel, i, color)
        
        render()

        time.sleep(0.002)
        elapsed_time = time.perf_counter() - elapsed_time

        if not loop:
            iterations -= 1

def color_wipe(color, wait):
    for i in range(LED_COUNT):
        ws.ws2811_led_set(channel, i, color)
        render()
        time.sleep(wait)

# Wrap following code in a try/finally to ensure cleanup functions are called
# after library is initialized.
try:
    # color_wipe(0xffffff, 0.05)
    disp_image(5000, matrix, loop=True)
finally:
    # Ensure ws2811_fini is called before the program quits.
    ws.ws2811_fini(leds)
    # Example of calling delete function to clean up structure memory.  Isn't
    # strictly necessary at the end of the program execution here, but is good practice.
    ws.delete_ws2811_t(leds)
