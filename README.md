# pyAMZN

pyAMZN is a tool that helps you retrieve a list of all your Amazon purchases for a given year and saves it as a CSV file.

## Useful Links

- If you find this project helpful, consider buying me a coffee: [Buy Me ☕](https://www.buymeacoffee.com/jgarza97885)
- Watch a video tutorial on how to use pyAMZN: [YouTube Tutorial ▶](https://youtu.be/1BCBll0lsiM)
- (Note: There's a planned tutorial for beginners that is not available yet)

> Note: Don't worry if you're new to programming, just keep practicing and you'll improve!

## Requirements

Before getting started, make sure you have the following:

- Python 3.0 or later installed. If you need help with the installation, you can search "How to install Python" on Google or ask for assistance from ChatGPT or Bard.
- Google Chrome web browser.
- Selenium Chrome Driver that matches your version of Chrome. You can download it from [here](https://chromedriver.chromium.org/downloads). (Note: There's already a driver file in the root directory, but it might not match your Chrome version.)
- An Amazon account.

## Setup and Execution

Follow these steps to set up and run pyAMZN:

1. Install the requirements mentioned above.
2. Run the command `pip install -r requirements.txt` to install some necessary Python libraries.
3. Edit the `passwords_example.json` file and replace the placeholder email and password with your own Amazon account credentials.
4. Rename the `passwords_example.json` file to `passwords.json`.
5. Run the `main.py` file. You can do this by opening a terminal, navigating to the project's directory, and running `py main.py` or `python main.py`. Alternatively, you can right-click the `main.py` file and select "Open with Python" from the context menu. (You can refer to the screenshot in the repository for clarification.)
6. If a CAPTCHA appears during the login process, you will need to solve it manually. After passing the CAPTCHA, return to the terminal window and press Enter to resume the program.
7. The program will take some time to complete, but once finished, it will save a CSV file in the root directory containing your Amazon purchase history.

## Frequently Asked Questions (FAQs)

### What should I do if I encounter a CAPTCHA?

If a CAPTCHA appears during the login process, the program will pause and wait for you to solve it manually. Once you have passed the CAPTCHA, go back to the terminal window and press Enter to allow the program to continue.

### How important is the Selenium Chrome Driver?

The Selenium Chrome Driver is essential for pyAMZN to interact with the Chrome browser. Make sure the version of the driver matches your installed version of Chrome. Please ensure that the `chromedriver.exe` file is located in the root directory of the project.

## Troubleshooting

If you encounter any issues while using pyAMZN, here are some common problems and their potential solutions:

- **Problem: Chrome version mismatch**  
  If you're experiencing compatibility issues with the Selenium Chrome Driver, it's likely due to a version mismatch between your installed Chrome browser and the driver. Make sure to download and use the appropriate version of the driver that matches your Chrome version.

- **Problem: Missing dependencies**  
  If you encounter import errors or other dependency-related issues, ensure that you have installed all the necessary Python libraries listed in the `requirements.txt` file. You can use the command `pip install -r requirements.txt` to install them automatically.

- **Problem: Captcha loop**  
  In rare cases, you might get stuck in a loop where the program keeps encountering CAPTCHAs during login. If this happens, try the following steps:
  1. Ensure you are providing the correct Amazon account credentials in the `passwords.json` file.
  2. Double-check your internet connection and try again.
  3. If the issue persists, consider temporarily disabling any VPN or proxy settings that might interfere with the login process.

If you still encounter problems that are not covered here, feel free to open an issue in the GitHub repository or seek help from the project's community.

## To-Do List

Here are some planned improvements for the project:

- [ ] Add logging support.
- [ ] Develop a user interface (UI) for easier interaction (low priority).
