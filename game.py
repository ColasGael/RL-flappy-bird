import numpy as np
import matplotlib.pyplot as plt

# method: is_collision (use occupancy grid)

if __name__ == '__main__':

    environment = Environment()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(environment.env)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis

    i, j = 0, 0
    
    def on_key(event):
        global i, j
        if event.key == "8":
            i = max(i-1,0)
        elif event.key == "2":
            i = min(i+1, 500)
        if event.key == "4":
            j = max(j-1,0)
        elif event.key == "6":
            j = min(j+1, 500)
        
        first_image[i,j] = 1
        im.set_data(first_image)
        plt.draw()
        print('you pressed', event.key, event.xdata, event.ydata)


    cid = fig.canvas.mpl_connect('key_press_event', on_key)


    
    def on_click(event):
        T = 10000

        for t in range(T):
            print("Frame:", t)
            #time.sleep(0)
            plt.pause(0.01)
            environment.scroll()
            im.set_data(environment.env)
            plt.draw()


    cid = fig.canvas.mpl_connect('button_press_event', on_click)
        
    #fig.canvas.mpl_disconnect(cid)

    plt.show()