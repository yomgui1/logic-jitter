#!/usr/bin/env python3
# requires: tinycss cssselect cairosvg pygal csv

import argparse
import pygal
import csv

def draw(file_csv, interrupt, gpio):
    xy_chart = pygal.XY(stroke=False, fill=False, show_y_labels=False, legend_at_bottom=True, show_dots=True, dots_size=0.8, print_values=False)
    xy_chart.title = 'Jiffies'

    interrupt_value = 0.0
    gpio_value      = 0.0
    dic             = []
    min_value       = 10
    max_value       = 0
    STEP_INIT       = 0
    STEP_INTERRUPT  = 1
    STEP_GPIO       = 2

    with open(file_csv, 'r') as csvfile:
        cvsreader = csv.reader(csvfile, delimiter=',')

        # the first entry give us the initial state
        init_state      = next(cvsreader)
        interrupt_state = init_state[interrupt]
        gpio_state      = init_state[gpio]
        step            = STEP_INIT
        
        for row in cvsreader:

            # The first step is to find an interrupt edge
            if step == STEP_INIT:
                if (interrupt_state == 0 and int(row[interrupt]) == 1):
                    interrupt_value = float(row[0])
                    step = STEP_INTERRUPT

            # The second step is to find a gpio commutation
            elif step == STEP_INTERRUPT:
                if (gpio_state != int(row[gpio])):
                    gpio_value = float(row[0])
                    step = STEP_GPIO

            # here we know we have an interrupt edge value
            # and the gpio commutation time
            # we can take the delay mesure between the two
            elif step == STEP_GPIO:
                delay = gpio_value - interrupt_value

                # store the delay value in millisecond.
                dic.append((delay * 1000, 0.5))

                # we want to keep in mind the min and max
                # delay.
                if delay < min_value:
                    min_value = delay
                if delay > max_value:
                    max_value = delay

                # we can now reinit the step
                step = STEP_INIT

            interrupt_state = int(row[interrupt])
            gpio_state      = int(row[gpio])

    print("min delay = ", min_value * 1000)
    print("max delay = ", max_value * 1000)

    xy_chart.add('values in millisecond', sorted(dic))
    xy_chart.render_to_png('jitter.png')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='file to parse')
    parser.add_argument('interrupt', help='the row in the csv file where is your interrupt pulse', type=int)
    parser.add_argument('gpio', help='the row in the csv file where is your gpio line', type=int)
    args = parser.parse_args()
    if not args.file or not args.interrupt or not args.gpio:
        print(args)

    draw(args.file, args.interrupt, args.gpio)
