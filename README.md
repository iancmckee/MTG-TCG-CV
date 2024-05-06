# MTG Card Reader/ Price Display - Computer Vision
This application was built as a hobby project and demoed on my [youtube channel](https://youtu.be/BZGhRSajybk?si=Lgs9nrcdm0YHqU0q&t=76) 

## System settings
**Python version:** 3.10 \
**Camera:** [IPEVO Camera](https://www.amazon.com/IPEVO-Definition-Document-Camera-5-880-4-01-00/dp/B079DLTG9F/ref=asc_df_B079DLTG9F/?tag=hyprod-20&linkCode=df0&hvadid=693308325727&hvpos=&hvnetw=g&hvrand=5970037353037000460&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9021712&hvtargid=pla-461670822372&mcid=546b320b9aaa30e883930a1bf2a7b555&gad_source=1&gclid=CjwKCAjw3NyxBhBmEiwAyofDYTbfEdHpdyFF3lRrCuXPoxbP8ZQASyoDxkeL_OPOeCFe-gjfA9e1OBoCBNMQAvD_BwE&th=1)
## Requirements:
you need to install the following items before the system will work, but you know this...
### Libraries
setup your virtual env by running `pip install -r requirements.txt` from the base folder
### Tesseract
You'll have to install tesseract onto your machine, I've downloaded it from [this source for windows](https://github.com/UB-Mannheim/tesseract/wiki)

## How to use
The system works best with a high contract background from the cards. The logic is that it just parses for the top 
portion of the card and reads the text, then matches it with the card with the most similar text.

The system will start up and identify any camera's you have accessible on your system. If there's more than one camera 
on your system, a dialog box should pop up allowing you to select by name.

next the system will prompt you to choose a set. The sets should be sorted by release date. Select a set and the system 
will star parsing all the prices from that NOTE: **THIS WILL TAKE A LONG TIME** - I have far from optimized anything 
involved in the scraping for this program, and would welcome any sort of improvements as PRs :)

press q anytime while the screen is active to deactivate it. 

##Troubleshooting:
**Threshold 1:** lower bound for [Canny Edge Detection](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html) \
**Threshold 2:** upper bound for Canny Edge Detection \
**Area:** represents the expected area for the rectangle of the card, again, feel free to play around with this

if your cards are not being identified, i'd recommend playing around with the sliders with the "Full Explanation" frame on. 
You'll notice that the lower threshold 1 is and the closer threshold 2 is to threshold 1, the more clarity you can get, but also the more "noise"
If you're using the camera linked above, it should be linked to values that should work.


Please have fun and enjoy using/building this system! 