from create_app import create_app
import sys


if __name__ == "__main__":
    try:
        port = sys.argv[1]
    except:
        port = 8001

    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=port)
