import warnings
warnings.filterwarnings("ignore", message=".*fitz.*API is deprecated.*", category=UserWarning)

import src.app as app

def main():
    app.run()


if __name__ == "__main__":
    main()